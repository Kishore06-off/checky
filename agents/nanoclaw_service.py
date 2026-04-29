"""
NanoClaw Agent Service for GovCheck AI
Integrates agentic AI capabilities without disrupting existing pipeline
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import os
from datetime import datetime

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AgentRequest(BaseModel):
    agent_type: str
    task: str
    data: Dict[str, Any]
    user_id: str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float
    timestamp: str

class NanoClawService:
    """
    NanoClaw integration service for GovCheck AI
    Handles agentic AI tasks as separate microservice
    """
    
    def __init__(self):
        self.base_url = os.getenv("NANOCLAW_SERVICE_URL", "http://localhost:3001")
        self.timeout = int(os.getenv("NANOCLAW_TIMEOUT_SEC", "30"))
        self.enabled = os.getenv("NANOCLAW_ENABLED", "true").lower() == "true"
        
        # Agent configurations directory
        self.agents_dir = Path(__file__).parent / "configs"
        self.agents_dir.mkdir(exist_ok=True)
        
        logger.info(f"NanoClaw service initialized - Enabled: {self.enabled}, URL: {self.base_url}")
    
    async def call_agent(self, request: AgentRequest) -> AgentResponse:
        """
        Call a NanoClaw agent with the specified task
        """
        if not self.enabled:
            return AgentResponse(
                success=False,
                error="NanoClaw service is disabled",
                processing_time=0.0,
                timestamp=datetime.utcnow().isoformat()
            )
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/agent/{request.agent_type}",
                    json={
                        "task": request.task,
                        "data": request.data,
                        "user_id": request.user_id,
                        "context": request.context or {}
                    }
                )
                
                processing_time = asyncio.get_event_loop().time() - start_time
                
                if response.status_code == 200:
                    result_data = response.json()
                    return AgentResponse(
                        success=True,
                        result=result_data.get("result"),
                        processing_time=processing_time,
                        timestamp=datetime.utcnow().isoformat()
                    )
                else:
                    return AgentResponse(
                        success=False,
                        error=f"Agent service error: {response.status_code}",
                        processing_time=processing_time,
                        timestamp=datetime.utcnow().isoformat()
                    )
                    
        except httpx.TimeoutException:
            return AgentResponse(
                success=False,
                error="Agent service timeout",
                processing_time=asyncio.get_event_loop().time() - start_time,
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Agent service error: {str(e)}",
                processing_time=asyncio.get_event_loop().time() - start_time,
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def enhance_checklist(self, checklist_data: List[Dict], user_id: str, document_context: str) -> AgentResponse:
        """
        Use NanoClaw agent to enhance generated checklist with additional insights
        """
        request = AgentRequest(
            agent_type="checklist_enhancer",
            task="enhance_compliance_checklist",
            data={
                "checklist_items": checklist_data,
                "document_context": document_context,
                "enhancement_types": ["risk_assessment", "implementation_guidance", "priority_scoring"]
            },
            user_id=user_id
        )
        
        return await self.call_agent(request)
    
    async def validate_compliance(self, checklist_data: List[Dict], user_id: str, compliance_framework: str = "GDPR") -> AgentResponse:
        """
        Use NanoClaw agent to validate checklist against specific compliance framework
        """
        request = AgentRequest(
            agent_type="compliance_validator",
            task="validate_framework_compliance",
            data={
                "checklist_items": checklist_data,
                "framework": compliance_framework,
                "validation_level": "comprehensive"
            },
            user_id=user_id
        )
        
        return await self.call_agent(request)
    
    async def generate_alerts(self, checklist_data: List[Dict], user_id: str, severity_threshold: str = "high") -> AgentResponse:
        """
        Use NanoClaw agent to generate compliance alerts for critical items
        """
        request = AgentRequest(
            agent_type="alert_generator",
            task="generate_compliance_alerts",
            data={
                "checklist_items": checklist_data,
                "severity_threshold": severity_threshold,
                "alert_types": ["missing_requirements", "critical_gaps", "deadline_violations"]
            },
            user_id=user_id
        )
        
        return await self.call_agent(request)
    
    async def analyze_document_risks(self, document_content: str, user_id: str, risk_categories: List[str] = None) -> AgentResponse:
        """
        Use NanoClaw agent to analyze document for potential compliance risks
        """
        if risk_categories is None:
            risk_categories = ["data_privacy", "security", "operational", "legal"]
        
        request = AgentRequest(
            agent_type="risk_analyzer",
            task="analyze_document_risks",
            data={
                "document_content": document_content,
                "risk_categories": risk_categories,
                "analysis_depth": "comprehensive"
            },
            user_id=user_id
        )
        
        return await self.call_agent(request)

# Global service instance
nanoclaw_service = NanoClawService()
