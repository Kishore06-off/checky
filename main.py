from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import os
import uuid
from typing import Optional
import gc

# Setup directories
os.makedirs("frontend", exist_ok=True)
os.makedirs("./output", exist_ok=True)

app = FastAPI(title="Governance AI API", version="2.0")

# CORS for frontend decoupling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import threading

def _prewarm_model():
    try:
        print("Pre-warming embedding model (background thread)...")
        from embedding.embedder import get_model
        get_model()
        print("Embedding model ready.")
    except Exception as e:
        print(f"Warning: Model pre-warm failed: {e}")

# Startup: Init db immediately; warm model in background so server starts fast
@app.on_event("startup")
async def startup_event():
    print("Initializing Database...")
    from storage.db import init_db
    init_db()
    # Warm model in background thread — server accepts requests immediately
    t = threading.Thread(target=_prewarm_model, daemon=True)
    t.start()
    print("Server ready. Model warming up in background...")

from celery_app import celery_app
from job_status import get_job_status, set_job_status
from queue_tasks import run_ingestion_pipeline

# Import NanoClaw agent service
try:
    from agents.nanoclaw_service import nanoclaw_service
except ImportError:
    nanoclaw_service = None
    print("Warning: NanoClaw agent service not available")
from ingestion_pipeline import execute_ingestion_pipeline

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
UPLOAD_CHUNK_SIZE_BYTES = int(os.getenv("UPLOAD_CHUNK_SIZE_BYTES", str(1024 * 1024)))
CHECKLIST_TOP_K = int(os.getenv("CHECKLIST_TOP_K", "12"))
CHAT_TOP_K = int(os.getenv("CHAT_TOP_K", "5"))

class ChatRequest(BaseModel):
    query: str
    domain: Optional[str] = "all"
    user_id: Optional[str] = "anonymous"


class RetrievalDebugRequest(BaseModel):
    query: str
    domain: Optional[str] = "all"
    user_id: Optional[str] = "anonymous"
    top_k: Optional[int] = 8

def _run_ingestion_fallback(file_path: str, filename: str, job_id: str, user_id: str) -> None:
    fallback_task_id = f"local-{job_id}"
    execute_ingestion_pipeline(
        file_path=file_path,
        filename=filename,
        job_id=job_id,
        user_id=user_id,
        task_id=fallback_task_id,
    )
    gc.collect()


@app.post("/api/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    link: Optional[str] = Form(None),
    user_id: str = Form("anonymous"),
):
    job_id = str(uuid.uuid4())
    os.makedirs(f"output/{user_id}", exist_ok=True)
    
    if link:
        # Process as a cloud link / webpage
        file_path = link
        filename = link
    elif file:
        # Process as a physical file upload
        file_path = os.path.join(f"output/{user_id}", f"{job_id}_{file.filename}")
        with open(file_path, "wb") as f:
            total_bytes = 0
            while True:
                chunk = await file.read(UPLOAD_CHUNK_SIZE_BYTES)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_UPLOAD_MB * 1024 * 1024:
                    f.close()
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds max upload limit of {MAX_UPLOAD_MB} MB",
                    )
                f.write(chunk)
        filename = file.filename
    else:
        raise HTTPException(status_code=400, detail="Must provide either a file or a link")

    try:
        # Force fallback mode for now due to Celery issues
        raise Exception("Forcing fallback mode")
        
        set_job_status(job_id, "queued", 0, "Job queued")
        task = run_ingestion_pipeline.delay(file_path, filename, job_id, user_id)
        set_job_status(job_id, "queued", 0, "Job queued", task_id=task.id)
        return {"job_id": job_id, "task_id": task.id, "message": "Upload successful, queued for background processing"}
    except Exception:
        # Fallback mode for local/dev environments where Redis/Celery is unavailable.
        fallback_task_id = f"local-{job_id}"
        set_job_status(
            job_id,
            "queued",
            0,
            "Queue unavailable, running local background processor",
            task_id=fallback_task_id,
        )
        background_tasks.add_task(_run_ingestion_fallback, file_path, filename, job_id, user_id)
        return {
            "job_id": job_id,
            "task_id": fallback_task_id,
            "message": "Upload successful, running local background processing",
            "mode": "local-fallback",
        }

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    status = get_job_status(job_id)
    if status:
        return status

    # Best-effort fallback: if status record has expired but result backend still has task state
    raise HTTPException(status_code=404, detail="Job not found")


@app.get("/api/system/memory")
async def memory_settings():
    return {
        "max_upload_mb": MAX_UPLOAD_MB,
        "upload_chunk_size_bytes": UPLOAD_CHUNK_SIZE_BYTES,
        "local_status_ttl_sec": int(os.getenv("LOCAL_JOB_STATUS_TTL_SEC", "3600")),
        "local_status_max_items": int(os.getenv("LOCAL_JOB_STATUS_MAX_ITEMS", "2000")),
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    from retrieval.retriever import retrieve_and_format
    from llm.generator import generate_answer, generate_checklist

    query_lower = request.query.lower()
    is_checklist = (
        "checklist" in query_lower
        or "extract all compliance policies" in query_lower
        or "strictly format as json" in query_lower
    )
    
    # Keep retrieval bounded to avoid checklist latency spikes.
    fetch_amount = CHECKLIST_TOP_K if is_checklist else CHAT_TOP_K
    results, context_string = await run_in_threadpool(
        retrieve_and_format, request.query, request.domain, top_k=fetch_amount, user_id=request.user_id
    )

    if not results or not context_string:
        return {"response": "No relevant context found in documents. Please ensure valid governance documents are uploaded and indexed."}

    if is_checklist:
        checklist_items = await run_in_threadpool(generate_checklist, context_string, results)
        if not checklist_items:
            return {"response": "Failed to generate structured checklist from the context.", "raw_data": None}

        # Format the JSON items into a beautiful markdown string for Streamlit UI
        from storage.db import save_checklist
        save_checklist(request.query, checklist_items, request.user_id)

        # Enhance checklist with NanoClaw agents if available
        enhanced_checklist = checklist_items
        if nanoclaw_service:
            try:
                # Risk analysis
                risk_result = await nanoclaw_service.analyze_document_risks(
                    context_string, request.user_id
                )
                
                # Checklist enhancement
                enhance_result = await nanoclaw_service.enhance_checklist(
                    checklist_items, request.user_id, context_string
                )
                
                # Compliance validation
                validation_result = await nanoclaw_service.validate_compliance(
                    checklist_items, request.user_id
                )
                
                # Alert generation
                alert_result = await nanoclaw_service.generate_alerts(
                    checklist_items, request.user_id
                )
                
                # Combine results if successful
                if enhance_result.success and enhance_result.result:
                    enhanced_checklist = enhance_result.result.get("enhanced_checklist", checklist_items)
                
                # Add agent insights to response metadata
                agent_insights = {
                    "risk_analysis": risk_result.result if risk_result.success else None,
                    "validation": validation_result.result if validation_result.success else None,
                    "alerts": alert_result.result if alert_result.success else None
                }
                
            except Exception as e:
                print(f"NanoClaw agent error: {e}")
                agent_insights = None
        else:
            agent_insights = None

        md_lines = ["### Compliance Extraction Request\n"]
        for it in enhanced_checklist:
            md_lines.append(f"- **Domain:** {it.get('domain', 'general').capitalize()}\n  **Requirement:** {it.get('item', '')}")
            if it.get("source_section") and it.get("source_section") not in ["â", "ââ"]:  
                md_lines.append(f"  *(Source Section: {it['source_section']})*")

        answer_string = "\n".join(md_lines)
        return {"response": answer_string, "raw_data": enhanced_checklist, "agent_insights": agent_insights}
    else:
        # Otherwise, use standard Chat Q&A
        answer_string = await run_in_threadpool(generate_answer, request.query, context_string)
        return {"response": answer_string, "raw_data": None}

@app.post("/api/chat/stream")
async def chat_endpoint_stream(request: ChatRequest):
    from retrieval.retriever import retrieve_and_format
    from llm.generator import stream_answer
    from fastapi.responses import StreamingResponse

    # EFFICIENCY FIX: Non-blocking threadpool offloaded execution
    results, context_string = await run_in_threadpool(
        retrieve_and_format, request.query, request.domain, top_k=5, user_id=request.user_id
    )

    if not results or not context_string:
        async def mock_stream():
            yield "No relevant context found in documents. Please ensure valid governance documents are uploaded and indexed."
        return StreamingResponse(mock_stream(), media_type="text/plain")

    # Use standard Chat Q&A via stream
    generator = stream_answer(request.query, context_string)
    
    async def generate():
        for chunk in generator:
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/debug/retrieval")
async def debug_retrieval(request: RetrievalDebugRequest):
    from retrieval.retriever import retrieve, summarize_sentence_hits

    top_k = max(1, min(int(request.top_k or 8), 30))
    results = await run_in_threadpool(
        retrieve,
        request.query,
        request.domain,
        None,
        None,
        top_k,
        request.user_id,
    )
    return {
        "query": request.query,
        "count": len(results),
        "hits": summarize_sentence_hits(results),
    }

# NanoClaw Agent Endpoints
@app.post("/api/agents/enhance-checklist")
async def enhance_checklist_agent(checklist_data: list[dict], user_id: str, document_context: str):
    """Enhance checklist using NanoClaw agents"""
    if not nanoclaw_service:
        raise HTTPException(status_code=503, detail="NanoClaw service not available")
    
    result = await nanoclaw_service.enhance_checklist(checklist_data, user_id, document_context)
    return result

@app.post("/api/agents/validate-compliance")
async def validate_compliance_agent(checklist_data: list[dict], user_id: str, compliance_framework: str = "GDPR"):
    """Validate compliance using NanoClaw agents"""
    if not nanoclaw_service:
        raise HTTPException(status_code=503, detail="NanoClaw service not available")
    
    result = await nanoclaw_service.validate_compliance(checklist_data, user_id, compliance_framework)
    return result

@app.post("/api/agents/generate-alerts")
async def generate_alerts_agent(checklist_data: list[dict], user_id: str, severity_threshold: str = "high"):
    """Generate compliance alerts using NanoClaw agents"""
    if not nanoclaw_service:
        raise HTTPException(status_code=503, detail="NanoClaw service not available")
    
    result = await nanoclaw_service.generate_alerts(checklist_data, user_id, severity_threshold)
    return result

@app.post("/api/agents/analyze-risks")
async def analyze_risks_agent(document_content: str, user_id: str, risk_categories: list[str] = None):
    """Analyze document risks using NanoClaw agents"""
    if not nanoclaw_service:
        raise HTTPException(status_code=503, detail="NanoClaw service not available")
    
    result = await nanoclaw_service.analyze_document_risks(document_content, user_id, risk_categories)
    return result

@app.get("/health")
async def health_check():
    """Health check endpoint for Render and monitoring"""
    return {
        "status": "ok",
        "service": "GovCheck AI API",
        "version": "2.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GovCheck AI API - Zero Hallucination Compliance System",
        "health": "/health",
        "docs": "/docs",
        "version": "2.0"
    }

@app.get("/api/agents/status")
async def agent_status():
    """Check NanoClaw agent service status"""
    return {
        "available": nanoclaw_service is not None,
        "enabled": nanoclaw_service.enabled if nanoclaw_service else False,
        "service_url": nanoclaw_service.base_url if nanoclaw_service else None,
        "agents": ["checklist_enhancer", "compliance_validator", "alert_generator", "risk_analyzer"]
    }

# Static frontend disabled - using Streamlit app.py instead
# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

