#!/usr/bin/env python3
"""
Minimal Flask app for testing Railway deployment
"""

from flask import Flask, jsonify
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Diksha Fundraising Backend API - Test Version",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "service": "Diksha Fundraising Backend - Test",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Get port from environment variable (Railway requirement)
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
