from flask import Flask, jsonify, request
from services.gsc_service import fetch_gsc_performance
from services.ga4_service import fetch_ga4_growth
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
        data = fetch_gsc_performance()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ga4-growth', methods=['GET'])
def ga4_growth():
    """Returns GA4 Metric Growth (MoM)."""
    try:
        data = fetch_ga4_growth()
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

# Vercel Serverless Entry Point
# Note: Vercel looks for 'app' by default in index.py
if __name__ == '__main__':
    app.run(debug=True)
