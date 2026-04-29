# NanoClaw Agent Integration for GovCheck AI

## Overview

This directory contains the NanoClaw agentic AI framework integration for GovCheck AI. The integration adds intelligent agent capabilities to enhance compliance analysis without disrupting the existing pipeline.

## Architecture

```
GovCheck AI Pipeline
    |
    |-- FastAPI Main Service
    |   |-- Document Ingestion (existing)
    |   |-- RAG Processing (existing)
    |   |-- Checklist Generation (existing)
    |   |-- NanoClaw Agent Integration (NEW)
    |       |-- Checklist Enhancement
    |       |-- Compliance Validation
    |       |-- Risk Analysis
    |       |-- Alert Generation
    |
    |-- NanoClaw Agent Service (separate microservice)
    |   |-- Checklist Enhancer Agent
    |   |-- Compliance Validator Agent
    |   |-- Alert Generator Agent
    |   |-- Risk Analyzer Agent
```

## Files Structure

```
agents/
|-- nanoclaw_service.py          # Main integration service
|-- nanoclaw_mock_service.py     # Mock service for testing
|-- configs/                     # Agent SOUL.md configurations
|   |-- checklist_enhancer.md
|   |-- compliance_validator.md
|   |-- alert_generator.md
|   |-- risk_analyzer.md
|-- README.md                    # This file
```

## Installation & Setup

### 1. Install Dependencies

```bash
pip install httpx
```

### 2. Configure Environment

Add to your `.env` file:
```env
# NanoClaw Agent Service Configuration
NANOCLAW_ENABLED=true
NANOCLAW_SERVICE_URL=http://localhost:3001
NANOCLAW_TIMEOUT_SEC=30
```

### 3. Start the Mock Service (for testing)

```bash
cd agents
python nanoclaw_mock_service.py
```

This starts a mock NanoClaw service on port 3001 that provides realistic responses for testing.

### 4. Restart Main Service

```bash
# Restart your FastAPI service to pick up the new integration
py -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Usage

### Automatic Integration

The NanoClaw agents are automatically integrated into the existing `/api/chat` endpoint when generating checklists. No changes needed to existing workflows.

### Direct Agent Access

You can also call agents directly via new endpoints:

#### Enhance Checklist
```bash
POST /api/agents/enhance-checklist
{
  "checklist_data": [...],
  "user_id": "user123",
  "document_context": "Document text..."
}
```

#### Validate Compliance
```bash
POST /api/agents/validate-compliance
{
  "checklist_data": [...],
  "user_id": "user123",
  "compliance_framework": "GDPR"
}
```

#### Generate Alerts
```bash
POST /api/agents/generate-alerts
{
  "checklist_data": [...],
  "user_id": "user123",
  "severity_threshold": "high"
}
```

#### Analyze Risks
```bash
POST /api/agents/analyze-risks
{
  "document_content": "Document text...",
  "user_id": "user123",
  "risk_categories": ["data_privacy", "security"]
}
```

#### Check Service Status
```bash
GET /api/agents/status
```

## Agent Capabilities

### 1. Checklist Enhancer Agent
- **Purpose**: Enhances generated checklists with risk assessments and implementation guidance
- **Features**:
  - Risk level assessment (high/medium/low)
  - Priority scoring (1-10)
  - Implementation guidance
  - Timeline estimation
  - Resource requirements
  - Compliance gap identification

### 2. Compliance Validator Agent
- **Purpose**: Validates checklists against specific regulatory frameworks
- **Frameworks**: GDPR, SOX, HIPAA, PCI DSS, ISO 27001
- **Features**:
  - Framework-specific validation
  - Regulatory reference mapping
  - Compliance scoring
  - Gap identification
  - Violation risk assessment

### 3. Alert Generator Agent
- **Purpose**: Generates actionable alerts for critical compliance issues
- **Features**:
  - Critical compliance gap alerts
  - Missing requirement detection
  - Priority-based classification
  - Actionable remediation steps
  - Timeline recommendations

### 4. Risk Analyzer Agent
- **Purpose**: Analyzes documents for potential compliance risks
- **Categories**: Data privacy, security, operational, legal
- **Features**:
  - Multi-dimensional risk assessment
  - Risk probability and impact analysis
  - Risk scoring and prioritization
  - Mitigation strategy recommendations

## Response Format

All agents return structured JSON responses that include:
- Success/error status
- Processing time
- Timestamp
- Structured results specific to each agent type

Example enhanced response in chat API:
```json
{
  "response": "### Compliance Extraction Request\n- **Domain:** Data Privacy\n  **Requirement:** Identify lawful basis...",
  "raw_data": [...],
  "agent_insights": {
    "risk_analysis": {...},
    "validation": {...},
    "alerts": {...}
  }
}
```

## Production Deployment

For production use, replace the mock service with the actual NanoClaw implementation:

1. Deploy NanoClaw agents on separate infrastructure
2. Update `NANOCLAW_SERVICE_URL` to point to production service
3. Configure proper authentication and security
4. Set up monitoring and logging

## Security Considerations

- Agents run in separate microservice for isolation
- No direct database access - operates via API only
- Configurable timeouts prevent hanging requests
- Graceful fallback when service unavailable
- All agent communications logged

## Troubleshooting

### Service Unavailable
If NanoClaw service is down, the system gracefully degrades to standard functionality.

### Timeout Issues
Increase `NANOCLAW_TIMEOUT_SEC` in environment variables.

### Integration Problems
Check service status via `/api/agents/status` endpoint.

## Benefits

1. **Zero Disruption**: Existing pipeline continues working unchanged
2. **Enhanced Analysis**: Deeper compliance insights and risk assessments
3. **Scalable**: Separate microservice can scale independently
4. **Flexible**: Easy to enable/disable per environment
5. **Future-Proof**: Can add new agent types without core changes

## Next Steps

1. Test with mock service to validate integration
2. Develop production NanoClaw agents based on SOUL.md configs
3. Deploy to staging environment
4. Monitor performance and accuracy
5. Gradual rollout to production
