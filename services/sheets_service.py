from googleapiclient.discovery import build
from .auth import get_credentials

def fetch_content_log(spreadsheet_id='1KL7Yvnytlb_ErsfO0lgDczR5Calkx620nzQONjGfrIU'):
    """
    Fetches Content Log and Site Health from Google Sheets.
    """
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    try:
        sheet = client.open("Filing Buddy Content Engine & SEO Setup").worksheet("Content_Log")
        data = sheet.get_all_records()
        
        # Columns: Date, Activity_Type, Platform, Content_Title_Topic, Status, Link, Metric_Views, Metric_Engagement
        
        activities = []
        total_views = 0
        
        for row in data:
            if str(row.get('Status', '')).lower() == 'published':
                try:
                    views = int(str(row.get('Metric_Views', 0)).replace(',',''))
                except:
                    views = 0
                
                total_views += views
                
                activities.append({
                    "date": row.get('Date', ''),
                    "type": row.get('Activity_Type', ''),
                    "platform": row.get('Platform', ''),
                    "title": row.get('Content_Title_Topic', ''),
                    "status": row.get('Status', ''),
                    "views": views,
                    "engagement": row.get('Metric_Engagement', 0),
                    "link": row.get('Link', '#')
                })
        
        # Sort by Date desc (assuming date strings sortable YYYY-MM-DD, otherwise relying on sheet order)
        # For robustness, we just take the top ones from the sheet if sorted, or sort locally
        # activities.sort(key=lambda x: x['date'], reverse=True) 

        # Fetch Health Score
        health_sheet = client.open("Filing Buddy Content Engine & SEO Setup").worksheet("Site_Health")
        health_score = health_sheet.acell('B2').value

        return {
            "health_score": health_score,
            "total_views": total_views,
            "activities": activities[:50] # Return up to 50 recent items
        }

    except Exception as e:
        print(f"Sheets Error: {e}")
        return {"health_score": 0, "activities": [], "error": str(e)}
```
