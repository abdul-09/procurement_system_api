import pandas as pd
from .models import Tender, Bid, VendorPerformance, SpendAnalytics

def generate_tender_report():
    bids = Bid.objects.select_related('tender').all()
    df = pd.DataFrame.from_records(bids.values('tender__title', 'price', 'submitted_at'))
    report = df.groupby('tender__title').agg({'price': 'sum', 'submitted_at': 'count'})
    report.columns = ['total_value', 'total_bids']
    return report

# def generate_vendor_performance():
#     vendors = VendorPerformance.objects.all()
#     df = pd.DataFrame.from_records(vendors.values('vendor__business_name', 'average_delivery_time', 'rating'))
#     performance_summary = df.groupby('vendor__business_name').mean()
#     return performance_summary
def generate_vendor_performance():
    # Query all vendor performance records
    vendors = VendorPerformance.objects.all()
    
    # Convert queryset to DataFrame, selecting relevant fields
    df = pd.DataFrame.from_records(
        vendors.values('vendor__business_name', 'average_delivery_time', 'rating')
    )
    
    # Group by vendor name and calculate mean for delivery time and rating
    if not df.empty:  # Check to prevent errors if the DataFrame is empty
        performance_summary = df.groupby('vendor__business_name').mean()
    else:
        performance_summary = pd.DataFrame()  # Return an empty DataFrame if no data
    
    return performance_summary

# def generate_spend_report():
#     spend_data = SpendAnalytics.objects.all()
#     df = pd.DataFrame.from_records(spend_data.values('category', 'total_spent', 'month'))
#     monthly_spend = df.groupby(['month', 'category']).sum().unstack()
#     return monthly_spend

def generate_spend_report():
    # Query all spend analytics data
    spend_data = SpendAnalytics.objects.all()
    
    # Convert queryset to DataFrame, selecting relevant fields
    df = pd.DataFrame.from_records(
        spend_data.values('category', 'total_spent', 'month')
    )
    
    # Group by month and category and sum up total spend
    if not df.empty:  # Check to prevent errors if the DataFrame is empty
        monthly_spend = df.groupby(['month', 'category']).sum().unstack()
    else:
        monthly_spend = pd.DataFrame()  # Return an empty DataFrame if no data
    
    return monthly_spend


import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

def create_tender_dashboard(report_data):
    app = dash.Dash(__name__)

    df = pd.DataFrame(report_data)

    app.layout = html.Div([
        dcc.Graph(
            id='tender-graph',
            figure={
                'data': [
                    {'x': df['tender__title'], 'y': df['total_value'], 'type': 'bar', 'name': 'Total Value'},
                    {'x': df['tender__title'], 'y': df['total_bids'], 'type': 'bar', 'name': 'Total Bids'},
                ],
                'layout': {
                    'title': 'Tender Report'
                }
            }
        )
    ])

    return app


import matplotlib.pyplot as plt

def generate_vendor_performance_chart(performance_data):
    vendors = performance_data['vendor']
    ratings = performance_data['rating']

    plt.bar(vendors, ratings)
    plt.title("Vendor Performance")
    plt.xlabel("Vendor")
    plt.ylabel("Rating")
    plt.show()
