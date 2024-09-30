import pandas as pd
from .models import Tender, Bid

def generate_tender_report():
    tenders = Tender.objects.all()
    data = []
    for tender in tenders:
        bids = tender.bids.all()
        total_bids = bids.count()
        total_value = bids.aggregate(total_value=pd.Sum('price'))['total_value']
        data.append([tender.title, total_bids, total_value])
    
    return pd.DataFrame(data, columns=['Tender', 'Total Bids', 'Total Value']).set_index('Tender')

def generate_tender_report():
    bids = Bid.objects.select_related('tender').all()
    df = pd.DataFrame.from_records(bids.values('tender__title', 'price', 'submitted_at'))
    report = df.groupby('tender__title').agg({'price': 'sum', 'submitted_at': 'count'})
    report.columns = ['total_value', 'total_bids']
    return report
