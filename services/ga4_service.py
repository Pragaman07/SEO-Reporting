from datetime import date, timedelta
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    Filter,
    OrderBy
)
)
from .auth import get_credentials

def fetch_ga4_growth(property_id='414531202'):
    """
    Fetches GA4 Metrics for Current Month vs Previous Month.
    Calculates % Growth (Delta).
    Filtered for 'Organic Search'.
    """
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)
    
    # 1. Date Logic (Last 30 days vs Previous 30 days)
    today = date.today()
    end_date = today
    start_date = end_date - timedelta(days=29) # 30 days total
    
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - timedelta(days=29)

    # 2. Build Request Function
    def get_metrics(start, end):
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="sessionDefaultChannelGroup")], # To filter
            metrics=[
                Metric(name="newUsers"),
                Metric(name="sessions"),
                Metric(name="userEngagementDuration"), # Total sec
                Metric(name="activeUsers") # For avg calculation
            ],
            date_ranges=[DateRange(start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d"))],
        )
        return client.run_report(req)

    # 3. Fetch Data
    curr_resp = get_metrics(start_date, end_date)
    prev_resp = get_metrics(prev_start_date, prev_end_date)
    
    def parse_organic(response):
        for row in response.rows:
            channel = row.dimension_values[0].value
            if "Organic Search" in channel:
                active_users = int(row.metric_values[3].value)
                total_duration = float(row.metric_values[2].value)
                avg_time = total_duration / active_users if active_users > 0 else 0
                
                return {
                    'newUsers': int(row.metric_values[0].value),
                    'sessions': int(row.metric_values[1].value),
                    'avgEngagementTime': int(avg_time) # in seconds
                }
        return {'newUsers': 0, 'sessions': 0, 'avgEngagementTime': 0}

    current = parse_organic(curr_resp)
    previous = parse_organic(prev_resp)
    
    # 4. Calculate Deltas
    def calc_delta(curr, prev):
        if prev == 0: return 100 if curr > 0 else 0
        return round(((curr - prev) / prev) * 100, 1)

    return {
        'newUsers': {
            'value': current['newUsers'],
            'delta': calc_delta(current['newUsers'], previous['newUsers'])
        },
        'sessions': {
            'value': current['sessions'],
            'delta': calc_delta(current['sessions'], previous['sessions'])
        },
        'avgEngagementTime': {
            'value': f"{current['avgEngagementTime'] // 60}m {current['avgEngagementTime'] % 60}s",
            'delta': calc_delta(current['avgEngagementTime'], previous['avgEngagementTime'])
        }
    }

def fetch_ga4_trend(start_date=None, end_date=None):
    """Fetches daily trend for new users and sessions (Organic Search)."""
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)
    
    # Defaults if None
    if not start_date or not end_date:
        today = date.today()
        end_date_obj = today
        start_date_obj = today - timedelta(days=29)
        start = start_date_obj.strftime("%Y-%m-%d")
        end = end_date_obj.strftime("%Y-%m-%d")
    else:
        start = start_date
        end = end_date

    request = RunReportRequest(
        property=f"properties/{os.environ.get('GA4_PROPERTY_ID', '315739343')}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="newUsers"), Metric(name="sessions")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="sessionDefaultChannelGroup",
                string_filter=Filter.StringFilter(value="Organic Search")
            )
        ),
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))]
    )
    
    response = client.run_report(request=request)
    
    trend_data = []
    for row in response.rows:
        # date comes as YYYYMMDD
        raw_date = row.dimension_values[0].value
        # Format to YYYY-MM-DD for easier JS parsing
        formatted_date = f"{raw_date[0:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
        
        trend_data.append({
            "date": formatted_date,
            "users": int(row.metric_values[0].value),
            "sessions": int(row.metric_values[1].value)
        })
        
    return trend_data
