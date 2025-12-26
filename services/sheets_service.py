import gspread
from .auth import get_credentials

def fetch_content_log():
    """
    Fetches Content Log and Site Health from Google Sheets using gspread.
    Returns: { "health_score": int, "total_views": int, "activities": list }
    """
    try:
        # 1. Authorize gspread
        creds = get_credentials()
        client = gspread.authorize(creds)

        # 2. Open Workbook
        # Ideally use ID if possible, but Name is fine if unique
        # Using ID is safer: 1KL7Yvnytlb_ErsfO0lgDczR5Calkx620nzQONjGfrIU
        wb = client.open_by_key('1KL7Yvnytlb_ErsfO0lgDczR5Calkx620nzQONjGfrIU')
        
        # 3. Fetch Content Log
        sheet_log = wb.worksheet("Content_Log")
        data = sheet_log.get_all_records()
        
        activities = []
        total_views = 0
        
        for row in data:
            # Check Status
            status = str(row.get('Status', '')).strip()
            if status.lower() == 'published':
                # Parse Views
                try:
                    views_str = str(row.get('Metric_Views', 0)).replace(',', '')
                    views = int(views_str) if views_str.isdigit() else 0
                except:
                    views = 0
                
                total_views += views
                
                activities.append({
                    "date": str(row.get('Date', '')),
                    "type": str(row.get('Activity_Type', '')),
                    "platform": str(row.get('Platform', '')),
                    "title": str(row.get('Content_Title_Topic', '')),
                    "status": status,
                    "views": views,
                    "engagement": str(row.get('Metric_Engagement', 0)),
                    "link": str(row.get('Link', '#'))
                })
        
        # 4. Fetch Health Score
        sheet_health = wb.worksheet("Site_Health")
        # Assuming B2 holds the score
        health_score_val = sheet_health.acell('B2').value
        
        return {
            "health_score": health_score_val,
            "total_views": total_views,
            "activities": activities[:50] # Top 50
        }

    except Exception as e:
        print(f"Sheets Error: {e}")
        return {"health_score": 0, "activities": [], "error": str(e)}
