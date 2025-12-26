from googleapiclient.discovery import build
from .auth import get_credentials

def fetch_content_log(spreadsheet_id='1KL7Yvnytlb_ErsfO0lgDczR5Calkx620nzQONjGfrIU'):
    """
    Fetches Content Log and Site Health from Google Sheets.
    """
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    try:
        # 1. Fetch Content Log (A:H)
        result_content = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range='Content_Log!A:H'
        ).execute()
        rows = result_content.get('values', [])
        
        # Simple processing: Filter 'Published' and sum Views (Traffic)
        activities = []
        total_views = 0
        
        # Skip header
        if len(rows) > 1:
            for row in rows[1:]:
                # Check for Publish Status (Column F -> index 5)
                if len(row) > 5 and row[5] == 'Published':
                    title = row[1] if len(row) > 1 else "Untitled"
                    views = int(row[6]) if len(row) > 6 and row[6].isdigit() else 0
                    
                    activities.append({'title': title, 'views': views})
                    total_views += views

        # 2. Fetch Health Score (Site_Health!A2)
        result_health = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range='Site_Health!A2'
        ).execute()
        health_row = result_health.get('values', [])
        health_score = int(health_row[0][0]) if health_row and health_row[0] else 0

        return {
            'activities': activities[:5], # Return top 5
            'total_views': total_views,
            'health_score': health_score
        }

    except Exception as e:
        print(f"Sheets Error: {e}")
        return {'activities': [], 'total_views': 0, 'health_score': 0}
