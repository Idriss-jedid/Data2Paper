"""
MCP Client for connecting to the database and retrieving data for AI report generation
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.db_schemes.schemes.task import Task
from models.db_schemes.schemes.user import User
from models.db_schemes.schemes.ai_report import AI_Report
from models.db_schemes.schemes.task_status_history import Task_Status_History
from models.enums.task_status import TaskStatus
from models.enums.report_type import ReportType

class MCPClient:
    """Model Context Protocol Client for database access"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def get_user_data(self, user_id: int) -> Optional[Dict]:
        """Retrieve user data"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    
    async def get_user_tasks(self, user_id: int, days: Optional[int] = None) -> List[Dict]:
        """Retrieve user tasks, optionally filtered by date range"""
        query = self.db.query(Task).filter(Task.user_id == user_id)
        
        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Task.created_at >= start_date)
        
        tasks = query.all()
        
        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            }
            for task in tasks
        ]
    
    async def get_task_status_history(self, task_id: int) -> List[Dict]:
        """Retrieve status history for a specific task"""
        history = self.db.query(Task_Status_History)\
                        .filter(Task_Status_History.task_id == task_id)\
                        .order_by(Task_Status_History.updated_at.asc())\
                        .all()
        
        return [
            {
                "id": h.id,
                "task_id": h.task_id,
                "status": h.status.value,
                "updated_at": h.updated_at.isoformat() if h.updated_at else None,
                "note": h.note
            }
            for h in history
        ]
    
    async def get_all_status_notes(self, task_id: int) -> List[Dict]:
        """Retrieve all notes from task status history for a specific task"""
        history = self.db.query(Task_Status_History)\
                        .filter(
                            and_(
                                Task_Status_History.task_id == task_id,
                                Task_Status_History.note.isnot(None)
                            )
                        )\
                        .order_by(Task_Status_History.updated_at.asc())\
                        .all()
        
        return [
            {
                "id": h.id,
                "task_id": h.task_id,
                "status": h.status.value,
                "updated_at": h.updated_at.isoformat() if h.updated_at else None,
                "note": h.note
            }
            for h in history
        ]
    
    async def get_user_tasks_with_history(self, user_id: int, days: Optional[int] = None) -> List[Dict]:
        """Retrieve user tasks with their status history"""
        tasks = await self.get_user_tasks(user_id, days)
        
        # Add status history to each task
        for task in tasks:
            # Ensure task is a dictionary before modifying it
            if isinstance(task, dict):
                task_id = task.get("id")
                if task_id is not None:
                    task["status_history"] = await self.get_task_status_history(task_id)
                    task["all_notes"] = await self.get_all_status_notes(task_id)
        
        return tasks
    
    async def get_task_statistics(self, user_id: int, period: str) -> Dict:
        """Get task statistics for a given period"""
        # Determine date range based on period
        if period == "daily":
            days = 1
        elif period == "weekly":
            days = 7
        elif period == "monthly":
            days = 30
        else:
            days = None  # All time
        
        tasks = await self.get_user_tasks(user_id, days)
        
        # Calculate statistics
        total_tasks = len(tasks)
        status_counts = {}
        completed_tasks = 0
        
        # Get status history for more detailed analysis
        status_changes = 0
        avg_completion_time = 0
        completion_times = []
        all_notes = []
        
        for task in tasks:
            # Ensure task is a dictionary
            if not isinstance(task, dict):
                continue
                
            status = task.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
            if status == TaskStatus.COMPLETED.value:
                completed_tasks += 1
                
            # Get status history for this task
            try:
                history = await self.get_task_status_history(task["id"])
                status_changes += len(history) - 1  # Exclude initial status
                
                # Get all status notes
                task_all_notes = await self.get_all_status_notes(task["id"])
                all_notes.extend(task_all_notes)
                
                # Calculate completion time if task is completed
                if status == TaskStatus.COMPLETED.value and len(history) > 1:
                    created_at_str = task.get("created_at")
                    if created_at_str:
                        try:
                            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                            completed_at = None
                            for h in history:
                                if isinstance(h, dict) and h.get("status") == TaskStatus.COMPLETED.value:
                                    updated_at_str = h.get("updated_at")
                                    if updated_at_str:
                                        try:
                                            completed_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                                            break
                                        except (ValueError, TypeError):
                                            continue
                            
                            if created_at and completed_at:
                                completion_time = (completed_at - created_at).total_seconds() / 3600  # In hours
                                completion_times.append(completion_time)
                        except (ValueError, TypeError):
                            pass  # Skip invalid date formats
            except Exception as e:
                print(f"Error processing task {task.get('id', 'unknown')}: {e}")
                # Continue with other tasks if there's an error with this one
                continue
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Additional statistics for weekly and monthly reports
        most_productive_day = ("N/A", 0)
        least_productive_day = ("N/A", 0)
        avg_tasks_per_day = 0
        
        if days:
            # Group tasks by day
            tasks_by_day = {}
            for task in tasks:
                if not isinstance(task, dict):
                    continue
                created_at_str = task.get("created_at")
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                        day_key = created_at.date().isoformat()
                        if day_key not in tasks_by_day:
                            tasks_by_day[day_key] = []
                        tasks_by_day[day_key].append(task)
                    except (ValueError, TypeError):
                        continue
            
            # Find most and least productive days
            if tasks_by_day:
                day_counts = {day: len(task_list) for day, task_list in tasks_by_day.items()}
                most_productive_day = max(day_counts.items(), key=lambda x: x[1]) if day_counts else ("N/A", 0)
                least_productive_day = min(day_counts.items(), key=lambda x: x[1]) if day_counts else ("N/A", 0)
                avg_tasks_per_day = sum(day_counts.values()) / len(day_counts) if day_counts else 0
        
        return {
            "period": period,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": status_counts.get(TaskStatus.IN_PROGRESS.value, 0),
            "pending_tasks": status_counts.get(TaskStatus.PENDING.value, 0),
            "overdue_tasks": status_counts.get(TaskStatus.OVERDUE.value, 0),
            "completion_rate": round(completion_rate, 2),
            "status_distribution": status_counts,
            "status_changes": status_changes,
            "avg_completion_time_hours": round(avg_completion_time, 2),
            "all_notes": all_notes,
            "most_productive_day": most_productive_day,
            "least_productive_day": least_productive_day,
            "avg_tasks_per_day": round(avg_tasks_per_day, 1)
        }
    
    async def get_recent_reports(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get recent reports for a user"""
        reports = self.db.query(AI_Report)\
            .filter(AI_Report.user_id == user_id)\
            .order_by(AI_Report.generated_at.desc())\
            .limit(limit)\
            .all()
        
        return [
            {
                "id": report.id,
                "report_type": report.report_type.value,
                "generated_at": report.generated_at.isoformat() if report.generated_at else None,
                "summary_text": report.summary_text[:100] + "..." if len(report.summary_text) > 100 else report.summary_text
            }
            for report in reports
        ]
    
    async def save_report(self, user_id: int, report_type: ReportType, summary_text: str, file_path: str = None) -> Dict:
        """Save a generated report to the database"""
        report = AI_Report(
            user_id=user_id,
            report_type=report_type,
            summary_text=summary_text,
            file_path=file_path
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return {
            "id": report.id,
            "user_id": report.user_id,
            "report_type": report.report_type.value,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
            "summary_text": report.summary_text,
            "file_path": report.file_path
        }

# Example usage
if __name__ == "__main__":
    pass