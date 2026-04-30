# Vercel-optimized Streamlit App for GovCheck AI
# This version is optimized for Vercel deployment

import streamlit as st
import time
import json
import requests
import os
import uuid
import pandas as pd

# Auto-detect API URL for Vercel
if os.getenv("ENVIRONMENT") == "production":
    # On Vercel, use the serverless function URL
    API_URL = os.getenv("VERCEL_URL", "")
    if API_URL:
        API_URL = f"https://{API_URL}/api"
    else:
        API_URL = os.getenv("API_URL", "https://your-app.vercel.app/api")
else:
    # Local development
    API_URL = os.getenv("API_URL", "http://localhost:8000")

# Debug logging
print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
print(f"API_URL: {API_URL}")

# Page config
st.set_page_config(
    page_title="GovCheck AI - Vercel",
    page_icon="https://cdn-icons-png.flaticon.com/512/4086/4086589.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">GovCheck AI - Zero Hallucination Compliance</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Configuration")
    
    # API URL input
    api_url_input = st.text_input("API URL", value=API_URL, key="api_url")
    
    # Debug info
    if st.checkbox("Show Debug Info"):
        st.json({
            "Environment": os.getenv("ENVIRONMENT", "development"),
            "API_URL": API_URL,
            "VERCEL_URL": os.getenv("VERCEL_URL", "Not set")
        })

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Upload Governance Document")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'txt', 'csv'],
        help="Upload your governance document for compliance analysis"
    )
    
    if uploaded_file:
        st.markdown(f"**File:** {uploaded_file.name}")
        st.markdown(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        
        # Process button
        if st.button("Process Document", type="primary"):
            with st.spinner("Processing document..."):
                try:
                    # Prepare file for upload
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        "user_id": str(uuid.uuid4()),
                        "domain": "governance"
                    }
                    
                    # Call API
                    response = requests.post(
                        f"{API_URL}/upload",
                        files=files,
                        data=data,
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Document processed successfully!")
                        
                        # Display results
                        with st.expander("View Results", expanded=True):
                            st.json(result)
                            
                    else:
                        st.error(f"Error: {response.status_code}")
                        st.error(response.text)
                        
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
                    st.markdown("#### Troubleshooting:")
                    st.markdown("1. Check if API URL is correct")
                    st.markdown("2. Verify API service is running")
                    st.markdown("3. Check environment variables")

with col2:
    st.markdown("### Features")
    
    st.markdown("""
    <div class="feature-card">
        <h4>Zero Hallucination</h4>
        <p>100% factually accurate compliance analysis with source verification</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h4>Real-time Processing</h4>
        <p>Fast document analysis with live progress updates</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h4>Source Verification</h4>
        <p>Every claim validated against source documents</p>
    </div>
    """, unsafe_allow_html=True)

# Test API connection
st.markdown("---")
st.markdown("### Test API Connection")

if st.button("Test API"):
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            st.success("API is working!")
            st.json(response.json())
        else:
            st.error(f"API returned: {response.status_code}")
    except Exception as e:
        st.error(f"Cannot connect to API: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>GovCheck AI - Powered by Zero-Hallucination Technology</p>
    <p>Deployed on Vercel Platform</p>
</div>
""", unsafe_allow_html=True)
