from fastapi import FastAPI, UploadFile, File, Form, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager, AsyncExitStack
from resume2practice.agent.nodes import (
  ResumeProfiler,
  JobDescriptionProfiler,
  ScorecardGenerator,
  TaskGenerator
)
from resume2practice.agent.graphs import Resume2Practice
from langgraph.types import Command
from io import BytesIO
from pypdf import PdfReader
from typing import Optional, Dict, Any
import json
import os

# -- Configuration ------------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set up agent to run alongside lifespan of server app
    resume_profiler_model = os.environ.get("RESUME_PROFILER_MODEL", os.environ.get("LLM_MODEL_ID", "gpt-4.1-mini"))
    resume_profiler_vendor = os.environ.get("RESUME_PROFILER_VENDOR", os.environ.get("LLM_VENDOR_ID", "openai"))
    resume_profiler = ResumeProfiler(vendor=resume_profiler_vendor, model_id=resume_profiler_model)
    job_description_model = os.environ.get("JOB_DESCRIPTION_PROFILER_MODEL", os.environ.get("LLM_MODEL_ID", "gpt-4.1-mini"))
    job_description_vendor = os.environ.get("JOB_DESCRIPTION_PROFILER_VENDOR", os.environ.get("LLM_VENDOR_ID", "openai"))
    job_description_profiler = JobDescriptionProfiler(vendor=job_description_vendor, model_id=job_description_model)
    scorecard_generator_model = os.environ.get("SCORECARD_GENERATOR_MODEL", os.environ.get("LLM_MODEL_ID", "gpt-4.1-mini"))
    scorecard_generator_vendor = os.environ.get("SCORECARD_GENERATOR_VENDOR", os.environ.get("LLM_VENDOR_ID", "openai"))
    scorecard_generator = ScorecardGenerator(vendor=scorecard_generator_vendor, model_id=scorecard_generator_model)
    task_generator_model = os.environ.get("TASK_GENERATOR_MODEL", os.environ.get("LLM_MODEL_ID", "gpt-4.1-mini"))
    task_generator_vendor = os.environ.get("TASK_GENERATOR_VENDOR", os.environ.get("LLM_VENDOR_ID", "openai"))
    task_generator = TaskGenerator(vendor=task_generator_vendor, model_id=task_generator_model)
    workflow = Resume2Practice(resume_profiler_chain=resume_profiler, 
                               job_description_profiler_chain=job_description_profiler, 
                               scorecard_generator_chain=scorecard_generator, 
                               task_generator_chain=task_generator)
    app.state.agent = workflow
    yield

app = FastAPI(lifespan=lifespan)

frontend_url = os.environ.get("FRONTEND_CLIENT_URL", "http://frontend:8888")
app.add_middleware(
    CORSMiddleware,
    allow_origins = [frontend_url],
    allow_credentials = True,
    allow_methods = ["GET", "POST"],
    allow_headers = ["*"]
)

# -- Helper functions ---------------------------
def extract_text_from_pdf(pdf: bytes) -> str:
    reader = PdfReader(BytesIO(pdf))
    pages = [
        page.extract_text() for page in reader.pages
    ]
    return "\n".join(pages)

# -- Routes --------------------------------
@app.get("/health")
async def health():
    """Get the health status of the server"""
    return JSONResponse(
        content={"status": "ok"}
    )

@app.post("/analyze")
async def analyze(
    thread_id: str = Form(...),
    job_description_text: Optional[str] = Form(None),
    job_description_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None)
    ):
    # -- Extract content from request payload
    # Handle uploaded resumes
    resume_content = ""
    if resume_file is not None:
        if resume_file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed for resume upload.")
        try:
            pdf_content = await resume_file.read()
            resume_content = extract_text_from_pdf(pdf_content)
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(ex)}")
    else:
        resume_content = resume_text
    
    # Handle uploaded job descriptions
    job_description_content = ""
    if job_description_file is not None:
        if job_description_file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed for job description upload")
        try:
            pdf_content = await job_description_file.read()
            job_description_content = extract_text_from_pdf(pdf_content)
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(ex)}")
    else:
        job_description_content = job_description_text

    # -- Send payload to agent for initial response
    context = {
        "resume": resume_content,
        "job_description": job_description_content
    }
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    response = await app.state.agent.ainvoke(context=context, config=config)

    # Return the state of the interrupt
    return JSONResponse(content=json.loads(response["__interrupt__"][0].value))

@app.post("/resume")
async def resume(data: Dict[str, Any]):
    """Resumes the AI workflow from where it left off"""
    try:
        config = {
            "configurable": {
                "thread_id": data["thread_id"]
            }
        }
    except IndexError:
        raise HTTPException(status_code=400, detail="Missing `thread_id` - cannot resume")
    try:
        result = await app.state.agent.ainvoke(
            context=Command(resume=data.get("response", "")), 
            config=config
        )

        final_result = {
            "scorecard": result["scorecard"],
            "task_list": result["task_list"]
        }

        return JSONResponse(content=final_result)
    except Exception as ex:
        raise HTTPException(
            status_code=500, 
            detail=f"Unable to finish request due to the following exception: {str(ex)}"
        )
