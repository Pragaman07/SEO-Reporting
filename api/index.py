from flask import Flask, jsonify, request
from services.gsc_service import fetch_gsc_performance
from services.ga4_service import fetch_ga4_growth, fetch_ga4_trend
from services.sheets_service import fetch_content_log
import os

app = Flask(__name__)

# Error Handler
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": str(error)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

# --- API Endpoints ---

@app.route('/api/gsc-performance', methods=['GET'])
def gsc_performance():
    """Returns GSC Query Stats, Brand Split, and Rank Buckets."""
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        data = fetch_gsc_performance(start_date=start, end_date=end)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ga4-growth', methods=['GET'])
def ga4_growth():
    """Returns GA4 Metric Growth (MoM)."""
    try:
        # GA4 Service creates its own comparison dates based on reference date, 
        # but we can pass current range logic if expanded later.
        # For now, it calculates vs previous period internally.
        data = fetch_ga4_growth() 
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ga4-trend', methods=['GET'])
def ga4_trend():
    """Returns GA4 Daily Trend."""
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        data = fetch_ga4_trend(start_date=start, end_date=end)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/content-log', methods=['GET'])
def content_log():
    """Returns Content Activities and Health Score."""
    try:
        data = fetch_content_log()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug', methods=['GET'])
def debug():
    """Checks environment setup."""
    token_present = 'GOOGLE_TOKEN' in os.environ
    creds_present = 'GOOGLE_CREDENTIALS' in os.environ
    try:
        from services.auth import get_credentials
        get_credentials()
        auth_status = "OK"
    except Exception as e:
        auth_status = f"Error: {str(e)}"
        
    return jsonify({
        "google_token_env": token_present,
        "google_credentials_env": creds_present,
        "auth_test": auth_status
    })

# Vercel Serverless Entry Point
# Note: Vercel looks for 'app' by default in index.py
if __name__ == '__main__':
    app.run(debug=True)
