# GovCheck AI - Deployment Guide

## Overview

GovCheck AI can be deployed for free on several platforms. This guide covers the best options and step-by-step instructions.

## Quick Start Options

### 1. Railway (Recommended - Easiest)
**Best for:** Beginners, quick deployment
**Free Tier:** $5/month credit, 500 hours/month

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy from project root
railway up
```

### 2. Render (Great Alternative)
**Best for:** Full-stack apps with databases
**Free Tier:** 750 hours/month, sleeps after 15min inactivity

1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Use the provided `render.yaml` configuration
4. Deploy automatically

### 3. Fly.io (Advanced)
**Best for:** Global deployment, custom domains
**Free Tier:** 160 shared CPU-hours/month

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
fly launch
fly deploy
```

## Platform-Specific Instructions

### Railway Deployment

1. **Prerequisites**
   - Railway account
   - GitHub repository (already created: https://github.com/Kishore06-off/checky)

2. **Setup**
   ```bash
   # Clone your repo
   git clone https://github.com/Kishore06-off/checky.git
   cd checky
   
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Deploy
   railway up
   ```

3. **Environment Variables**
   Set these in Railway dashboard:
   - `GROQ_API_KEY`: Your Groq API key
   - `REDIS_URL`: Railway Redis connection string
   - `SECRET_KEY`: Random secret key

### Render Deployment

1. **Prerequisites**
   - Render account
   - GitHub repository

2. **Setup**
   - Connect GitHub to Render
   - Use `deploy/render.yaml` configuration
   - Render will automatically detect and deploy

3. **Services Created**
   - `govcheck-api`: FastAPI backend
   - `govcheck-ui`: Streamlit frontend
   - `govcheck-chroma`: Vector database

### Fly.io Deployment

1. **Prerequisites**
   - Fly.io account
   - Fly CLI installed

2. **Setup**
   ```bash
   # Clone repo
   git clone https://github.com/Kishore06-off/checky.git
   cd checky
   
   # Launch app
   fly launch
   
   # Deploy
   fly deploy
   ```

3. **Database Setup**
   ```bash
   # Deploy ChromaDB
   fly deploy --config deploy/fly.toml
   ```

### Docker Deployment (Self-Hosting)

1. **Build Docker Image**
   ```bash
   docker build -t govcheck-ai .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Manual Docker Run**
   ```bash
   docker run -p 8000:8000 -p 8501:8501 \
     -e GROQ_API_KEY=your_key \
     -e REDIS_URL=redis://localhost:6379 \
     govcheck-ai
   ```

## Environment Variables

### Required Variables
```bash
# LLM API
GROQ_API_KEY=your_groq_api_key

# Database
REDIS_URL=redis://localhost:6379
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Security
SECRET_KEY=your_secret_key_here
```

### Optional Variables
```bash
# Performance
MAX_WORKERS=4
EMBEDDING_BATCH_SIZE=512

# Features
NANOCLAW_ENABLED=false
GROUNDING_VALIDATION_ENABLED=true
GROUNDING_MIN_CONFIDENCE=0.8
```

## Free Tier Limitations

| Platform | CPU | Memory | Storage | Bandwidth | Limitations |
|----------|-----|---------|---------|-----------|-------------|
| Railway | Shared | 512MB | 1GB | 100GB | $5 credit |
| Render | Shared | 512MB | 10GB | 100GB | Sleeps after 15min |
| Fly.io | Shared | 256MB | 3GB | 100GB | 160 hours/month |
| Vercel | Function | 1GB | 100GB | 100GB | Static only |
| AWS EC2 | 1 vCPU | 1GB | 8GB | 750GB | 750 hours |

## Production Checklist

### Security
- [ ] Set strong `SECRET_KEY`
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Set appropriate CORS origins

### Performance
- [ ] Configure Redis for caching
- [ ] Set up ChromaDB persistence
- [ ] Monitor resource usage
- [ ] Set up logging

### Monitoring
- [ ] Add health checks
- [ ] Set up alerting
- [ ] Monitor API usage
- [ ] Track error rates

## Troubleshooting

### Common Issues

1. **Out of Memory**
   - Reduce `EMBEDDING_BATCH_SIZE`
   - Limit concurrent workers
   - Use smaller models

2. **Slow Startup**
   - Use Docker layer caching
   - Pre-download models
   - Optimize imports

3. **Database Connection**
   - Check Redis URL format
   - Verify ChromaDB connectivity
   - Check firewall settings

### Platform-Specific Issues

**Railway**
- Check credit balance
- Verify environment variables
- Review build logs

**Render**
- Check sleep timer settings
- Verify database connections
- Review service health

**Fly.io**
- Check region availability
- Verify volume mounts
- Review networking config

## Scaling Considerations

### When to Upgrade
- Consistent high memory usage
- Frequent rate limiting
- Slow response times
- High error rates

### Paid Tier Benefits
- More CPU/memory
- No sleep timers
- Custom domains
- Better support

## Support

- **Documentation**: Check this guide and code comments
- **Issues**: Create GitHub issues
- **Community**: Join Discord/Slack communities
- **Platform Support**: Use platform-specific support channels

## Next Steps

1. Choose your deployment platform
2. Set up account and billing
3. Configure environment variables
4. Deploy using platform-specific instructions
5. Test all features
6. Monitor performance
7. Set up alerts and monitoring

Your GovCheck AI platform is now ready for production deployment!
