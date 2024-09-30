import pandas as pd
from .models import SpendAnalytics


def generate_spend_report():
    spend_data = SpendAnalytics.objects.all()
    df = pd.DataFrame.from_records(spend_data.values('category', 'total_spent', 'month'))
    monthly_spend = df.groupby(['month', 'category']).sum().unstack()
    return monthly_spend