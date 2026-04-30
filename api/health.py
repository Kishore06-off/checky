# Vercel serverless function for health check
# Minimal dependencies

import json
import os

def handler(request):
    """Health check endpoint"""
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "ok",
            "service": "GovCheck AI API",
            "version": "2.0",
            "environment": os.getenv("ENVIRONMENT", "production"),
            "platform": "vercel",
            "message": "Zero Hallucination Compliance System"
        })
    }

# Vercel expects a function named 'handler' at the top level
app = handler
