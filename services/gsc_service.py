from googleapiclient.discovery import build
from datetime import date, timedelta
import re
from .auth import get_credentials

def fetch_gsc_performance(site_url='https://filingbuddy.global/en-in/', start_date=None, end_date=None):
    """
    Fetches GSC Query Data and processes:
    - Branded vs Non-Branded Split
    - Rank Buckets
    - Overall Totals
    """
    creds = get_credentials()
    service = build('searchconsole', 'v1', credentials=creds)

    if not start_date:
        today = date.today()
        end_date = today.strftime("%Y-%m-%d")
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")

    # 1. Fetch Totals (Site Level)
    req_totals = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': [],
        'rowLimit': 1
    }
    
    totals = {'clicks': 0, 'impressions': 0, 'ctr': 0, 'position': 0}
    try:
        resp_totals = service.searchanalytics().query(siteUrl=site_url, body=req_totals).execute()
        if 'rows' in resp_totals:
            row = resp_totals['rows'][0]
            totals = {
                'clicks': row['clicks'],
                'impressions': row['impressions'],
                'ctr': row['ctr'],
                'position': row['position']
            }
    except Exception as e:
        print(f"GSC Totals Error: {e}")

    # 2. Fetch Query Level Data (for charts)
    req_query = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['query'],
        'rowLimit': 5000
    }
    
    try:
        resp_query = service.searchanalytics().query(siteUrl=site_url, body=req_query).execute()
        rows = resp_query.get('rows', [])
    except Exception as e:
        print(f"GSC Query Error: {e}")
        rows = []

    # 3. Processing
    brand_regex = r"(?i)(filing\s?buddy)" # Matches 'filing buddy', 'filingbuddy', etc.
    branded_imps = 0
    non_branded_imps = 0
    
    buckets = {
        '1-10': 0,
        '11-20': 0,
        '21-50': 0,
        '51-100': 0
    }
    
    top_queries = []

    for row in rows:
        query = row['keys'][0]
        imps = row['impressions']
        pos = row['position']
        
        # Brand Split
        if re.search(brand_regex, query):
            branded_imps += imps
        else:
            non_branded_imps += imps
            
        # Bucketing
        if pos <= 10: buckets['1-10'] += 1
        elif pos <= 20: buckets['11-20'] += 1
        elif pos <= 50: buckets['21-50'] += 1
        elif pos <= 100: buckets['51-100'] += 1
        
        # Top 5 Queries
        if len(top_queries) < 5:
            top_queries.append({
                'query': query,
                'clicks': row['clicks'],
                'impressions': imps,
                'position': round(pos, 1)
            })

    # Calculations
    total_imps_calc = branded_imps + non_branded_imps
    brand_share = round((branded_imps / total_imps_calc * 100), 1) if total_imps_calc > 0 else 0
    non_brand_share = round((non_branded_imps / total_imps_calc * 100), 1) if total_imps_calc > 0 else 0

    return {
        'totals': totals,
        'brand_split': {
            'branded_share': brand_share,
            'non_branded_share': non_brand_share
        },
        'buckets': buckets,
        'top_queries': top_queries
    }
