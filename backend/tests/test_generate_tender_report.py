from datetime import date, timedelta
import pytest
from api.report import generate_tender_report, generate_vendor_performance, generate_spend_report

@pytest.mark.django_db
def test_generate_tender_report(bid_data):
    report = generate_tender_report()

    assert report.shape[0] == 2  # 2 tenders
    assert 'Tender A' in report.index
    assert 'Tender B' in report.index

    tender_a_data = report.loc['Tender A']
    assert tender_a_data['total_bids'] == 2
    assert tender_a_data['total_value'] == 95000

    tender_b_data = report.loc['Tender B']
    assert tender_b_data['total_bids'] == 1
    assert tender_b_data['total_value'] == 60000

@pytest.mark.django_db
def test_generate_vendor_performance_report(vendor_performance_data):
    report = generate_vendor_performance()

    # Ensure that the vendor names exist in the report
    assert 'Vendor 1' in report.index
    assert 'Vendor 2' in report.index  # Adjust based on your fixture data

    # Check that the performance report has correct calculations
    assert report.loc['Vendor 1']['average_delivery_time'] == timedelta(days=5)
    assert report.loc['Vendor 2']['average_delivery_time'] == timedelta(days=7)
    assert report.loc['Vendor 1']['rating'] == 4.5
    assert report.loc['Vendor 2']['rating'] == 3.8


@pytest.mark.django_db
def test_generate_spend_analytics_report(spend_analytics_data):
    report = generate_spend_report()

    # Ensure that the categories exist in the report
    assert 'Office Supplies' in report.columns.get_level_values(1)
    assert 'Technology' in report.columns.get_level_values(1)

    # Check that the spend report has correct values
    assert date(2024, 8, 1) in report.index
    assert date(2024, 9, 1) in report.index

    assert report.loc[date(2024, 8, 1)]['total_spent']['Office Supplies'] == 50000
    assert report.loc[date(2024, 9, 1)]['total_spent']['Technology'] == 120000
