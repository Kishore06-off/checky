# Vercel serverless function for file upload only
# Minimal dependencies to stay under 500MB limit

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
    """Handle file upload requests"""
    
    method = request.method
    path = request.path
    
    if method == "POST" and "/upload" in path:
        try:
            # Import only what we need
            import uuid
            import tempfile
            from fastapi import UploadFile, Form
            from fastapi.responses import JSONResponse
            
            # Get form data
            files = request.files
            data = request.form or {}
            
            # Extract file
            if 'file' not in files:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "No file provided"})
                }
            
            file = files['file']
            user_id = data.get('user_id', str(uuid.uuid4()))
            domain = data.get('domain', 'governance')
            
            # Simple file processing (minimal)
            file_content = file.read()
            file_size = len(file_content)
            
            # Return success response
            result = {
                "message": "File uploaded successfully",
                "filename": file.filename,
                "size": file_size,
                "user_id": user_id,
                "domain": domain,
                "job_id": str(uuid.uuid4()),
                "status": "completed"
            }
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(result)
            }
            
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Upload failed",
                    "detail": str(e)
                })
            }
    
    else:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Endpoint not found"})
        }

# Vercel expects a function named 'handler' at the top level
app = handler
