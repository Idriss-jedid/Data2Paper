"""
AI Report routes for generating different types of reports using AI agents
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from database import get_db
from models.model.auth import get_current_active_user
from models.db_schemes.schemes.user import User
from agents.mcp_client import MCPClient
from agents.report_agent import ReportAgent

router = APIRouter(
    prefix="/ai-reports",
    tags=["ai-reports"],
    dependencies=[Depends(get_current_active_user)]
)

class CustomReportRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    task_filters: Dict[str, Any] = {}

class ReportResponse(BaseModel):
    report_id: int
    report_type: str
    generated_at: str
    summary: str
    details: Dict[str, Any]
    document_path: Optional[str] = None

class DocumentGenerationRequest(BaseModel):
    generate_document: bool = False

@router.post("/daily", response_model=ReportResponse)
async def generate_daily_report(
    doc_request: DocumentGenerationRequest = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a daily report for the current user"""
    try:
        generate_doc = doc_request.generate_document if doc_request else False
        
        mcp_client = MCPClient(db)
        report_agent = ReportAgent(mcp_client)
        
        report_data = await report_agent.generate_daily_report(current_user.id, generate_doc)
        
        return ReportResponse(
            report_id=report_data["report_id"],
            report_type=report_data["report_type"],
            generated_at=report_data["generated_at"],
            summary=report_data["summary"],
            details=report_data,
            document_path=report_data.get("document_path")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate daily report: {str(e)}")

@router.post("/weekly", response_model=ReportResponse)
async def generate_weekly_report(
    doc_request: DocumentGenerationRequest = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a weekly report for the current user"""
    try:
        generate_doc = doc_request.generate_document if doc_request else False
        
        mcp_client = MCPClient(db)
        report_agent = ReportAgent(mcp_client)
        
        report_data = await report_agent.generate_weekly_report(current_user.id, generate_doc)
        
        return ReportResponse(
            report_id=report_data["report_id"],
            report_type=report_data["report_type"],
            generated_at=report_data["generated_at"],
            summary=report_data["summary"],
            details=report_data,
            document_path=report_data.get("document_path")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate weekly report: {str(e)}")

@router.post("/monthly", response_model=ReportResponse)
async def generate_monthly_report(
    doc_request: DocumentGenerationRequest = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a monthly report for the current user"""
    try:
        generate_doc = doc_request.generate_document if doc_request else False
        
        mcp_client = MCPClient(db)
        report_agent = ReportAgent(mcp_client)
        
        report_data = await report_agent.generate_monthly_report(current_user.id, generate_doc)
        
        return ReportResponse(
            report_id=report_data["report_id"],
            report_type=report_data["report_type"],
            generated_at=report_data["generated_at"],
            summary=report_data["summary"],
            details=report_data,
            document_path=report_data.get("document_path")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate monthly report: {str(e)}")

@router.post("/custom", response_model=ReportResponse)
async def generate_custom_report(
    request: CustomReportRequest,
    doc_request: DocumentGenerationRequest = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a custom report for the current user based on parameters"""
    try:
        generate_doc = doc_request.generate_document if doc_request else False
        
        mcp_client = MCPClient(db)
        report_agent = ReportAgent(mcp_client)
        
        report_data = await report_agent.generate_custom_report(current_user.id, request.dict(), generate_doc)
        
        return ReportResponse(
            report_id=report_data["report_id"],
            report_type=report_data["report_type"],
            generated_at=report_data["generated_at"],
            summary=report_data["summary"],
            details=report_data,
            document_path=report_data.get("document_path")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate custom report: {str(e)}")

@router.get("/history")
async def get_report_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get report generation history for the current user"""
    try:
        mcp_client = MCPClient(db)
        reports = await mcp_client.get_recent_reports(current_user.id)
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report history: {str(e)}")