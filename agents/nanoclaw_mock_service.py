"""
Mock NanoClaw Service for Testing
Provides mock responses for NanoClaw agent integration
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

logger = logging.getLogger(__name__)

class AgentRequest(BaseModel):
    task: str
    data: Dict[str, Any]
    user_id: str
    context: Dict[str, Any] = {}

app = FastAPI(title="Mock NanoClaw Service", version="1.0")

@app.post("/api/agent/checklist_enhancer")
async def checklist_enhancer(request: AgentRequest):
    """Mock checklist enhancer agent"""
    checklist_items = request.data.get("checklist_items", [])
    
    enhanced_items = []
    for item in checklist_items:
        enhanced_item = dict(item)
        enhanced_item.update({
            "risk_level": "medium",
            "priority_score": 7,
            "implementation_guidance": "1. Assess current state 2. Define requirements 3. Implement controls 4. Monitor compliance",
            "estimated_timeline": "4-6 weeks",
            "resource_requirements": ["Staff", "Technology", "Budget"],
            "compliance_gaps": ["Documentation", "Training"],
            "dependencies": []
        })
        enhanced_items.append(enhanced_item)
    
    return {
        "enhanced_checklist": enhanced_items,
        "summary": {
            "total_items": len(enhanced_items),
            "high_risk_items": 1,
            "critical_gaps": 2,
            "estimated_total_effort": "8-12 person-weeks"
        }
    }

@app.post("/api/agent/compliance_validator")
async def compliance_validator(request: AgentRequest):
    """Mock compliance validator agent"""
    framework = request.data.get("framework", "GDPR")
    checklist_items = request.data.get("checklist_items", [])
    
    return {
        "validation_results": {
            "framework": framework,
            "overall_compliance_score": 75,
            "critical_issues": [
                {
                    "item_id": checklist_items[0].get("id", "unknown") if checklist_items else "unknown",
                    "severity": "medium",
                    "issue": "Missing documentation for data processing activities",
                    "regulatory_reference": "GDPR Article 30",
                    "remediation_required": "Implement comprehensive data processing inventory",
                    "deadline": "30 days"
                }
            ],
            "missing_requirements": [
                {
                    "requirement": "Data Protection Impact Assessment procedure",
                    "regulatory_basis": "GDPR Article 35",
                    "impact": "High-risk processing may not be properly assessed"
                }
            ],
            "validation_summary": {
                "total_items_checked": len(checklist_items),
                "compliant_items": len(checklist_items) - 1,
                "non_compliant_items": 1,
                "critical_gaps": 1,
                "recommendations": ["Enhance documentation", "Implement DPIA procedures"]
            }
        }
    }

@app.post("/api/agent/alert_generator")
async def alert_generator(request: AgentRequest):
    """Mock alert generator agent"""
    checklist_items = request.data.get("checklist_items", [])
    
    return {
        "alerts": [
            {
                "id": "alert_001",
                "severity": "high",
                "type": "missing_requirement",
                "title": "Missing Data Breach Notification Procedure",
                "description": "No documented procedure for notifying supervisory authority of data breaches",
                "checklist_item_id": checklist_items[0].get("id", "unknown") if checklist_items else "unknown",
                "regulatory_reference": "GDPR Article 33",
                "risk_impact": "Potential regulatory fines for delayed breach notification",
                "remediation_steps": ["Develop breach notification procedure", "Establish notification timeline", "Define breach assessment criteria"],
                "deadline": "21 days",
                "assigned_role": "Data Protection Officer",
                "dependencies": ["Incident response team"]
            }
        ],
        "alert_summary": {
            "total_alerts": 1,
            "critical_alerts": 0,
            "high_priority_alerts": 1,
            "medium_priority_alerts": 0,
            "low_priority_alerts": 0,
            "immediate_actions_required": 1,
            "estimated_resolution_time": "2-3 person-weeks"
        },
        "recommendations": [
            {
                "category": "strategic",
                "recommendation": "Implement comprehensive incident response framework",
                "priority": "high",
                "estimated_impact": "Reduced regulatory risk and improved compliance posture"
            }
        ]
    }

@app.post("/api/agent/risk_analyzer")
async def risk_analyzer(request: AgentRequest):
    """Mock risk analyzer agent"""
    document_content = request.data.get("document_content", "")
    risk_categories = request.data.get("risk_categories", ["data_privacy", "security", "operational", "legal"])
    
    return {
        "risk_analysis": {
            "overall_risk_score": 65,
            "risk_level": "medium",
            "risk_categories": {
                "data_privacy": {
                    "score": 70,
                    "risks": [
                        {
                            "id": "risk_001",
                            "title": "Insufficient Data Protection Measures",
                            "description": "Document lacks specific technical measures for data protection",
                            "probability": 7,
                            "impact": 8,
                            "risk_score": 56,
                            "evidence": ["No mention of encryption", "No access control specifications"],
                            "regulatory_references": ["GDPR Article 32"],
                            "mitigation_strategies": ["Implement encryption", "Define access controls", "Regular security audits"],
                            "timeline": "6-8 weeks"
                        }
                    ]
                },
                "security": {
                    "score": 60,
                    "risks": []
                },
                "operational": {
                    "score": 55,
                    "risks": []
                },
                "legal_regulatory": {
                    "score": 75,
                    "risks": []
                }
            },
            "top_risks": [
                {
                    "rank": 1,
                    "risk_title": "Insufficient Data Protection Measures",
                    "risk_score": 56,
                    "category": "data_privacy",
                    "immediate_actions": ["Conduct security assessment", "Implement encryption"]
                }
            ],
            "risk_trends": {
                "emerging_risks": ["AI governance", "Cloud compliance"],
                "improving_areas": ["Documentation practices"],
                "stable_risks": ["Data protection", "Access control"]
            },
            "recommendations": {
                "immediate_actions": [
                    {
                        "action": "Implement encryption for sensitive data",
                        "priority": "high",
                        "owner": "IT Security",
                        "timeline": "2-4 weeks"
                    }
                ],
                "strategic_improvements": [
                    {
                        "improvement": "Develop comprehensive data protection framework",
                        "expected_impact": "Significant risk reduction",
                        "implementation_complexity": "medium"
                    }
                ]
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Mock NanoClaw Service"
    }

if __name__ == "__main__":
    print("Starting Mock NanoClaw Service on port 3001...")
    print("This is a mock service for testing NanoClaw integration")
    uvicorn.run(app, host="127.0.0.1", port=3001, log_level="info")
