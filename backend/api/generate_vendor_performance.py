import pandas as pd
import matplotlib.pyplot as plt
from .models import VendorPerformance

def generate_vendor_performance_chart(performance_data):
    vendors = performance_data['vendor']
    ratings = performance_data['rating']

    plt.bar(vendors, ratings)
    plt.title("Vendor Performance")
    plt.xlabel("Vendor")
    plt.ylabel("Rating")
    plt.show()

def generate_vendor_performance():
    vendors = VendorPerformance.objects.all()
    df = pd.DataFrame.from_records(vendors.values('vendor__business_name', 'average_delivery_time', 'rating'))
    performance_summary = df.groupby('vendor__business_name').mean()
    return performance_summary