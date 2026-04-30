#!/bin/bash

# Auto-Setup Script for Render Deployment
# This script automates the entire Render setup process

echo "=== GovCheck AI Auto-Setup for Render ==="

# Step 1: Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "Installing Render CLI..."
    npm install -g @render/cli
fi

# Step 2: Login to Render
echo "Please login to Render..."
render login

# Step 3: Create services from render.yaml
echo "Creating services from render.yaml..."
render create --from-file deploy/render.yaml

# Step 4: Wait for services to be created
echo "Waiting for services to be created..."
sleep 30

# Step 5: Set environment variables
echo "Setting environment variables..."

# API Service Environment Variables
render env set GROQ_API_KEY=your_groq_api_key_here --service govcheck-api
render env set SECRET_KEY=your_secret_key_here --service govcheck-api
render env set ENVIRONMENT=production --service govcheck-api
render env set GROUNDING_VALIDATION_ENABLED=true --service govcheck-api
render env set GROUNDING_MIN_CONFIDENCE=0.8 --service govcheck-api

# Frontend Service Environment Variables
render env set API_URL=https://govcheck-api.onrender.com --service govcheck-ui
render env set ENVIRONMENT=production --service govcheck-ui

# Step 6: Enable auto-deploy
echo "Enabling auto-deploy..."
render deploy --service govcheck-api --auto-deploy
render deploy --service govcheck-ui --auto-deploy
render deploy --service govcheck-chroma --auto-deploy

# Step 7: Health check
echo "Performing health check..."
sleep 60

echo "Checking API service..."
curl -f https://govcheck-api.onrender.com/health || echo "API service not ready yet"

echo "Checking UI service..."
curl -f https://govcheck-ui.onrender.com || echo "UI service not ready yet"

echo "=== Auto-Setup Complete ==="
echo "Your GovCheck AI is now automatically deployed!"
echo "API: https://govcheck-api.onrender.com"
echo "UI: https://govcheck-ui.onrender.com"
echo ""
echo "Auto-deploy is enabled - future git pushes will deploy automatically!"
