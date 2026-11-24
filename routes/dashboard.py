
from datetime import date, datetime, timedelta
import calendar

from flask import Blueprint, render_template, request
from flask_login import login_required
from models import db, Sale, Product

dashboard_bp = Blueprint('dashboard', __name__)

# Your database stores sale timestamps in UTC.
# Convert them to Philippine time (UTC+8) for reports.
PH_OFFSET = timedelta(hours=8)


def to_utc(local_datetime):
    return local_datetime - PH_OFFSET


@dashboard_bp.route('/dashboard')
@login_required
def index():

    # Current Philippine date and time
    local_now = datetime.utcnow() + PH_OFFSET
    today = local_now.date()
    current_year = today.year

    # Read the selected reporting period
    period = request.args.get('period', 'this_week').strip().lower()
    print("SELECTED PERIOD:", period)

    if period not in ['today', 'this_week', 'this_month', 'this_year']:
        period = 'this_week'

    # Set the reporting period using Philippine dates
    if period == 'today':
        start_date = today
        end_date = today + timedelta(days=1)
        period_label = 'Today'

    elif period == 'this_week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=7)
        period_label = 'This Week'

    elif period == 'this_month':
        start_date = today.replace(day=1)

        if today.month == 12:
            end_date = date(today.year + 1, 1, 1)
        else:
            end_date = date(today.year, today.month + 1, 1)

        period_label = 'This Month'

    else:
        start_date = date(today.year, 1, 1)
        end_date = date(today.year + 1, 1, 1)
        period_label = 'This Year'

    # Convert Philippine date boundaries to UTC
    start_utc = to_utc(datetime.combine(start_date, datetime.min.time()))
    end_utc = to_utc(datetime.combine(end_date, datetime.min.time()))

    # Get sales inside the selected period
    period_sales = Sale.query.filter(
        Sale.transaction_date >= start_utc,
        Sale.transaction_date < end_utc
    ).all()

    # Summary cards: selected period
    total_revenue = sum(s.total_revenue for s in period_sales)
    total_profit = sum(s.total_profit for s in period_sales)
    total_products_sold = sum(s.quantity_sold for s in period_sales)
    number_of_transactions = len(period_sales)

    # Daily Sales Overview
    if period == 'today':
        daily_labels = [f'{hour:02d}:00' for hour in range(24)]
        daily_sales_data = [0.0] * 24

        for sale in period_sales:
            local_sale_time = sale.transaction_date + PH_OFFSET
            daily_sales_data[local_sale_time.hour] += sale.total_revenue

    elif period == 'this_week':
        daily_labels = []
        daily_sales_data = [0.0] * 7

        for offset in range(7):
            current_day = start_date + timedelta(days=offset)
            daily_labels.append(current_day.strftime('%a'))

        for sale in period_sales:
            local_sale_date = (
                sale.transaction_date + PH_OFFSET
            ).date()

            day_index = (local_sale_date - start_date).days
            if 0 <= day_index < 7:
                daily_sales_data[day_index] += sale.total_revenue

    elif period == 'this_month':
        days_in_month = calendar.monthrange(
            today.year, today.month
        )[1]

        daily_labels = [str(day) for day in range(1, days_in_month + 1)]
        daily_sales_data = [0.0] * days_in_month

        for sale in period_sales:
            local_sale_date = (
                sale.transaction_date + PH_OFFSET
            ).date()

            day_index = local_sale_date.day - 1
            daily_sales_data[day_index] += sale.total_revenue

    else:
        daily_labels = list(calendar.month_abbr)[1:]
        daily_sales_data = [0.0] * 12

        for sale in period_sales:
            local_sale_time = sale.transaction_date + PH_OFFSET
            month_index = local_sale_time.month - 1
            daily_sales_data[month_index] += sale.total_revenue

    # Monthly Revenue Overview: all 12 months of the selected year
    year_start = to_utc(datetime(current_year, 1, 1))
    year_end = to_utc(datetime(current_year + 1, 1, 1))

    year_sales = Sale.query.filter(
        Sale.transaction_date >= year_start,
        Sale.transaction_date < year_end
    ).all()

    monthly_labels = list(calendar.month_abbr)[1:]
    monthly_revenue_data = [0.0] * 12

    for sale in year_sales:
        local_sale_time = sale.transaction_date + PH_OFFSET
        month_index = local_sale_time.month - 1
        monthly_revenue_data[month_index] += sale.total_revenue

    # Product Sales Performance: top 10 products in selected period
    product_totals = {}

    for sale in period_sales:
        product_name = (
            sale.product.product_name
            if sale.product else 'Deleted Product'
        )

        product_totals[product_name] = (
            product_totals.get(product_name, 0) + sale.quantity_sold
        )

    top_products = sorted(
        product_totals.items(),
        key=lambda item: item[1],
        reverse=True
    )[:10]

    product_labels = [item[0] for item in top_products]
    product_sales_data = [item[1] for item in top_products]

    return render_template(
        'dashboard.html',
        total_revenue=total_revenue,
        total_profit=total_profit,
        total_products_sold=total_products_sold,
        number_of_transactions=number_of_transactions,
        daily_labels=daily_labels,
        daily_sales_data=daily_sales_data,
        monthly_labels=monthly_labels,
        monthly_revenue_data=monthly_revenue_data,
        product_labels=product_labels,
        product_sales_data=product_sales_data,
        current_year=current_year,
        selected_period=period,
        period_label=period_label
    )
