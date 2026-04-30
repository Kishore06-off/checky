# Vercel Serverless Function for GovCheck AI API
# This handles all API endpoints as serverless functions

import json
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for Vercel
os.environ["ENVIRONMENT"] = "production"

def handler(request):
    """Main handler for all API requests"""
    
    # Parse request
    method = request.method
    path = request.path
    headers = dict(request.headers)
    
    try:
        # Import FastAPI app
        from main import app
        from fastapi.testclient import TestClient
        
        # Create test client for serverless execution
        client = TestClient(app)
        
        # Convert Vercel request to FastAPI format
        if method == "GET":
            response = client.get(path)
        elif method == "POST":
            # Handle file uploads and JSON data
            if "multipart/form-data" in headers.get("content-type", ""):
                # File upload handling
                files = {}
                data = {}
                
                # Parse multipart form data
                content_type = headers.get("content-type", "")
                if "boundary=" in content_type:
                    boundary = content_type.split("boundary=")[1].strip()
                    # Simplified multipart parsing
                    body = request.body.decode('utf-8')
                    # This is a simplified version - you might need to enhance this
                    response = client.post(path, files=files, data=data)
                else:
                    response = client.post(path, json=request.json)
            else:
                response = client.post(path, json=request.json)
        elif method == "PUT":
            response = client.put(path, json=request.json)
        elif method == "DELETE":
            response = client.delete(path)
        else:
            return {
                "statusCode": 405,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Method not allowed"})
            }
        
        # Convert FastAPI response to Vercel format
        return {
            "statusCode": response.status_code,
            "headers": dict(response.headers),
            "body": response.content.decode('utf-8')
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Internal server error",
                "detail": str(e)
            })
        }

# Health check endpoint
def health_handler():
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "ok",
            "service": "GovCheck AI API",
            "version": "2.0",
            "environment": "production",
            "platform": "vercel"
        })
    }

# Root endpoint
def root_handler():
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "message": "GovCheck AI API - Zero Hallucination Compliance System",
            "health": "/api/health",
            "version": "2.0",
            "platform": "vercel"
        })
    }
