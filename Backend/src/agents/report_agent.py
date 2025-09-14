"""
AI Report Agent that uses MCP to access data and generate reports
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

# Import MCP client
from agents.mcp_client import MCPClient
from models.enums.report_type import ReportType

# Import LLM module
from llm.GeminiProvider import GeminiProvider

# Import document writer
from agents.doc_writer_agent import DocWriterAgent

# Import config
from config import settings


class ReportAgent:
    """AI Agent for generating different types of reports"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp = mcp_client
        self.llm_provider = None
        self.doc_writer = DocWriterAgent(output_dir="reports")
        
        # Initialize LLM provider if API key is available
        api_key = settings.gemini_api_key
        if api_key:
            try:
                self.llm_provider = GeminiProvider(api_key=api_key)
                self.llm_provider.set_generation_model("gemini-pro")
            except Exception as e:
                print(f"Failed to initialize LLM provider: {e}")
                self.llm_provider = None
    
    async def generate_daily_report(self, user_id: int, generate_doc: bool = False) -> Dict[str, Any]:
        """Generate a daily report for the user"""
        # Get user data
        user_data = await self.mcp.get_user_data(user_id)
        if not user_data:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get today's statistics
        stats = await self.mcp.get_task_statistics(user_id, "daily")
        
        # Get today's tasks with history
        tasks = await self.mcp.get_user_tasks_with_history(user_id, 1)
        
        # Generate AI summary
        summary = self._generate_daily_summary(user_data, stats, tasks)
        
        # Save report
        report = await self.mcp.save_report(
            user_id=user_id,
            report_type=ReportType.DAILY,
            summary_text=summary
        )
        
        result = {
            "report_id": report["id"],
            "report_type": "Daily",
            "generated_at": report["generated_at"],
            "summary": summary,
            "statistics": stats,
            "tasks": tasks
        }
        
        # Generate Word document if requested
        if generate_doc:
            try:
                doc_path = self.doc_writer.create_report_document(result, user_data)
                result["document_path"] = doc_path
            except Exception as e:
                print(f"Failed to generate Word document: {e}")
        
        return result
    
    async def generate_weekly_report(self, user_id: int, generate_doc: bool = False) -> Dict[str, Any]:
        """Generate a weekly report for the user"""
        # Get user data
        user_data = await self.mcp.get_user_data(user_id)
        if not user_data:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get weekly statistics
        stats = await self.mcp.get_task_statistics(user_id, "weekly")
        
        # Get weekly tasks with history
        tasks = await self.mcp.get_user_tasks_with_history(user_id, 7)
        
        # Generate AI summary
        summary = self._generate_weekly_summary(user_data, tasks, stats)
        
        # Save report
        report = await self.mcp.save_report(
            user_id=user_id,
            report_type=ReportType.WEEKLY,
            summary_text=summary
        )
        
        result = {
            "report_id": report["id"],
            "report_type": "Weekly",
            "generated_at": report["generated_at"],
            "summary": summary,
            "statistics": stats,
            "tasks": tasks
        }
        
        # Generate Word document if requested
        if generate_doc:
            try:
                doc_path = self.doc_writer.create_report_document(result, user_data)
                result["document_path"] = doc_path
            except Exception as e:
                print(f"Failed to generate Word document: {e}")
        
        return result
    
    async def generate_monthly_report(self, user_id: int, generate_doc: bool = False) -> Dict[str, Any]:
        """Generate a monthly report for the user"""
        # Get user data
        user_data = await self.mcp.get_user_data(user_id)
        if not user_data:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get monthly statistics
        stats = await self.mcp.get_task_statistics(user_id, "monthly")
        
        # Get monthly tasks with history
        tasks = await self.mcp.get_user_tasks_with_history(user_id, 30)
        
        # Generate AI summary
        summary = self._generate_monthly_summary(user_data, stats, tasks)
        
        # Save report
        report = await self.mcp.save_report(
            user_id=user_id,
            report_type=ReportType.MONTHLY,
            summary_text=summary
        )
        
        result = {
            "report_id": report["id"],
            "report_type": "Monthly",
            "generated_at": report["generated_at"],
            "summary": summary,
            "statistics": stats,
            "tasks": tasks
        }
        
        # Generate Word document if requested
        if generate_doc:
            try:
                doc_path = self.doc_writer.create_report_document(result, user_data)
                result["document_path"] = doc_path
            except Exception as e:
                print(f"Failed to generate Word document: {e}")
        
        return result
    
    async def generate_custom_report(self, user_id: int, parameters: Dict[str, Any], generate_doc: bool = False) -> Dict[str, Any]:
        """Generate a custom report based on parameters"""
        # Get user data
        user_data = await self.mcp.get_user_data(user_id)
        if not user_data:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Extract custom parameters
        start_date = parameters.get("start_date")
        end_date = parameters.get("end_date")
        task_filters = parameters.get("task_filters", {})
        
        # Get tasks based on custom parameters
        # This would need to be implemented in the MCP client
        tasks = await self.mcp.get_user_tasks_with_history(user_id)  # Simplified
        
        # Generate AI summary
        summary = self._generate_custom_summary(user_data, tasks, parameters)
        
        # Save report
        report = await self.mcp.save_report(
            user_id=user_id,
            report_type=ReportType.CUSTOM,
            summary_text=summary
        )
        
        result = {
            "report_id": report["id"],
            "report_type": "Custom",
            "generated_at": report["generated_at"],
            "summary": summary,
            "parameters": parameters,
            "tasks": tasks
        }
        
        # Generate Word document if requested
        if generate_doc:
            try:
                doc_path = self.doc_writer.create_custom_report_document(result, user_data)
                result["document_path"] = doc_path
            except Exception as e:
                print(f"Failed to generate Word document: {e}")
        
        return result
    
    def _generate_daily_summary(self, user_data: Dict, stats: Dict, tasks: List[Dict]) -> str:
        """Generate a daily summary using AI logic"""
        # Use LLM if available
        if self.llm_provider:
            try:
                # Safely access user data
                user_name = user_data.get('name', 'User') if isinstance(user_data, dict) else 'User'
                
                # Enhanced prompt with more context and structured analysis
                prompt = f"""
                As an AI Productivity Analyst, generate a comprehensive daily productivity report for {user_name}.
                
                USER PROFILE:
                Name: {user_name}
                Role: {user_data.get('role', 'N/A') if isinstance(user_data, dict) else 'N/A'}
                
                TODAY'S PRODUCTIVITY SNAPSHOT:
                - Total Tasks: {stats.get('total_tasks', 0) if isinstance(stats, dict) else 0}
                - Completed Tasks: {stats.get('completed_tasks', 0) if isinstance(stats, dict) else 0}
                - Completion Rate: {stats.get('completion_rate', 0) if isinstance(stats, dict) else 0}%
                - Status Distribution: {stats.get('status_distribution', {}) if isinstance(stats, dict) else {}}
                - Status Changes: {stats.get('status_changes', 0) if isinstance(stats, dict) else 0}
                
                TODAY'S TASK PORTFOLIO:
                {self._format_tasks_briefly(tasks[:10] if isinstance(tasks, list) else [])}
                
                CRITICAL INSIGHTS FROM STATUS NOTES:
                {self._format_all_notes(stats.get('all_notes', [])[:20] if isinstance(stats, dict) else [])}
                
                INSTRUCTIONS:
                1. Provide a professional executive summary (2-3 sentences) highlighting today's key achievements and areas for improvement
                2. Analyze productivity patterns and identify factors contributing to success or challenges
                3. Offer 3 specific, actionable recommendations for tomorrow based on today's performance
                4. Predict potential challenges for tomorrow based on today's unfinished tasks
                5. Suggest a focus area for tomorrow that aligns with the user's role and current task load
                6. Use a professional, encouraging tone with data-driven insights
                7. Format the response with clear sections: Executive Summary, Performance Analysis, Tomorrow's Recommendations, Focus Area
                """
                
                response = self.llm_provider.generate_text(prompt, max_output_tokens=1500, temperature=0.7)
                if response:
                    return response
            except Exception as e:
                print(f"Error generating summary with LLM: {e}")
        
        # Fallback to template-based summary
        # Safely access user data
        user_name = user_data.get('name', 'User') if isinstance(user_data, dict) else 'User'
        user_email = user_data.get('email', 'user@example.com') if isinstance(user_data, dict) else 'user@example.com'
        user_role = user_data.get('role', 'N/A') if isinstance(user_data, dict) else 'N/A'
        
        # Safely access stats data
        total_tasks = stats.get('total_tasks', 0) if isinstance(stats, dict) else 0
        completed_tasks = stats.get('completed_tasks', 0) if isinstance(stats, dict) else 0
        completion_rate = stats.get('completion_rate', 0) if isinstance(stats, dict) else 0
        status_distribution = stats.get('status_distribution', {}) if isinstance(stats, dict) else {}
        status_changes = stats.get('status_changes', 0) if isinstance(stats, dict) else 0
        all_notes = stats.get('all_notes', []) if isinstance(stats, dict) else []
        
        return f"""
DAILY PRODUCTIVITY REPORT
=========================

Prepared for: {user_name} ({user_email})
Role: {user_role}
Date: {datetime.now().strftime('%B %d, %Y')}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
-----------------
Today's productivity snapshot shows {total_tasks} active tasks with {completed_tasks} completed, 
resulting in a {completion_rate}% completion rate. There have been {status_changes} status 
updates across all tasks today.

TASK METRICS
------------
• Total Tasks: {total_tasks}
• Completed Tasks: {completed_tasks}
• In Progress: {status_distribution.get('In Progress', 0)}
• Pending: {status_distribution.get('Pending', 0)}
• Overdue: {status_distribution.get('Overdue', 0)}
• Completion Rate: {completion_rate}%

RECENT ACTIVITIES
-----------------
{self._format_tasks_briefly(tasks[:10] if isinstance(tasks, list) else [])}

STATUS NOTES
------------
{self._format_all_notes(all_notes[:15])}

KEY INSIGHTS
------------
1. Current focus should be on completing pending tasks to improve completion rate
2. Maintain momentum on in-progress tasks to ensure timely completion
3. Review any overdue tasks and adjust priorities if necessary

RECOMMENDATIONS
---------------
• Prioritize tasks that are closest to their deadline
• Break down complex tasks into smaller, manageable subtasks
• Schedule focused work time for high-priority items
        """.strip()
    
    def _generate_weekly_summary(self, user_data: Dict, tasks: list, stats: Dict) -> str:
        """Generate a weekly summary using AI logic"""
        # Use LLM if available
        if self.llm_provider:
            try:
                # Safely access user data
                user_name = user_data.get('name', 'User') if isinstance(user_data, dict) else 'User'
                user_role = user_data.get('role', 'N/A') if isinstance(user_data, dict) else 'N/A'
                
                # Enhanced prompt with more context and structured analysis
                prompt = f"""
                As an AI Productivity Consultant, generate a comprehensive weekly productivity analysis for {user_name}, who works as a {user_role}.
                
                USER PROFILE:
                Name: {user_name}
                Role: {user_role}
                
                WEEKLY PERFORMANCE DASHBOARD:
                - Total Tasks Managed: {stats.get('total_tasks', 0) if isinstance(stats, dict) else 0}
                - Tasks Completed: {stats.get('completed_tasks', 0) if isinstance(stats, dict) else 0}
                - Completion Rate: {stats.get('completion_rate', 0) if isinstance(stats, dict) else 0}%
                - Status Distribution: {stats.get('status_distribution', {}) if isinstance(stats, dict) else {}}
                - Status Updates: {stats.get('status_changes', 0) if isinstance(stats, dict) else 0}
                - Average Completion Time: {stats.get('avg_completion_time_hours', 0) if isinstance(stats, dict) else 0} hours
                
                PRODUCTIVITY PATTERNS ANALYSIS:
                - Most Productive Day: {stats.get('most_productive_day', ('N/A', 0))[0] if isinstance(stats, dict) and isinstance(stats.get('most_productive_day'), tuple) else 'N/A'} ({stats.get('most_productive_day', ('N/A', 0))[1] if isinstance(stats, dict) and isinstance(stats.get('most_productive_day'), tuple) else '0'} tasks)
                - Least Productive Day: {stats.get('least_productive_day', ('N/A', 0))[0] if isinstance(stats, dict) and isinstance(stats.get('least_productive_day'), tuple) else 'N/A'} ({stats.get('least_productive_day', ('N/A', 0))[1] if isinstance(stats, dict) and isinstance(stats.get('least_productive_day'), tuple) else '0'} tasks)
                - Average Daily Task Load: {stats.get('avg_tasks_per_day', 0) if isinstance(stats, dict) else 0:.1f} tasks
                
                SIGNIFICANT TASKS THIS WEEK:
                {self._format_tasks_briefly(tasks[:15] if isinstance(tasks, list) else [])}
                
                CRITICAL INSIGHTS FROM STATUS NOTES:
                {self._format_all_notes(stats.get('all_notes', [])[:30] if isinstance(stats, dict) else [])}
                
                INSTRUCTIONS:
                1. Provide a professional executive summary (3-4 sentences) highlighting this week's key achievements and productivity trends
                2. Analyze productivity patterns and identify factors contributing to peak performance days vs. low performance days
                3. Offer 4 specific, actionable recommendations for next week based on this week's performance
                4. Identify skill development opportunities based on task types and challenges encountered
                5. Predict potential challenges for next week based on unfinished tasks and patterns
                6. Suggest a strategic focus area for next week that aligns with the user's role and long-term goals
                7. Include a brief SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) based on the week's data
                8. Use a professional, data-driven tone with insights tailored to the user's role
                9. Format the response with clear sections: Executive Summary, Productivity Analysis, Next Week Recommendations, Strategic Focus, SWOT Analysis
                """
                
                response = self.llm_provider.generate_text(prompt, max_output_tokens=2000, temperature=0.7)
                if response:
                    return response
            except Exception as e:
                print(f"Error generating summary with LLM: {e}")
        
        # Fallback to template-based summary
        # Safely access user data
        user_name = user_data.get('name', 'User') if isinstance(user_data, dict) else 'User'
        user_email = user_data.get('email', 'user@example.com') if isinstance(user_data, dict) else 'user@example.com'
        user_role = user_data.get('role', 'N/A') if isinstance(user_data, dict) else 'N/A'
        
        # Safely access stats data
        total_tasks = stats.get('total_tasks', 0) if isinstance(stats, dict) else 0
        completed_tasks = stats.get('completed_tasks', 0) if isinstance(stats, dict) else 0
        in_progress_tasks = stats.get('in_progress_tasks', 0) if isinstance(stats, dict) else 0
        pending_tasks = stats.get('pending_tasks', 0) if isinstance(stats, dict) else 0
        overdue_tasks = stats.get('overdue_tasks', 0) if isinstance(stats, dict) else 0
        completion_rate = stats.get('completion_rate', 0) if isinstance(stats, dict) else 0
        status_distribution = stats.get('status_distribution', {}) if isinstance(stats, dict) else {}
        status_changes = stats.get('status_changes', 0) if isinstance(stats, dict) else 0
        avg_completion_time = stats.get('avg_completion_time_hours', 0) if isinstance(stats, dict) else 0
        most_productive_day = stats.get('most_productive_day', ('N/A', 0)) if isinstance(stats, dict) else ('N/A', 0)
        least_productive_day = stats.get('least_productive_day', ('N/A', 0)) if isinstance(stats, dict) else ('N/A', 0)
        avg_tasks_per_day = stats.get('avg_tasks_per_day', 0) if isinstance(stats, dict) else 0
        all_notes = stats.get('all_notes', []) if isinstance(stats, dict) else []
        
        return f"""
WEEKLY PRODUCTIVITY REPORT
==========================

Prepared for: {user_name} ({user_email})
Role: {user_role}
Period: Last 7 Days
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
-----------------
This week, you managed {total_tasks} tasks with {completed_tasks} completed, 
achieving a {completion_rate}% completion rate. You made {status_changes} status 
updates across all tasks, with an average completion time of {avg_completion_time} hours.

PRODUCTIVITY ANALYSIS
---------------------
• Most Productive Day: {most_productive_day[0]} ({most_productive_day[1]} tasks)
• Least Productive Day: {least_productive_day[0]} ({least_productive_day[1]} tasks)
• Average Daily Task Load: {avg_tasks_per_day} tasks
• In Progress: {in_progress_tasks}
• Pending: {pending_tasks}
• Overdue: {overdue_tasks}

SIGNIFICANT TASKS
-----------------
{self._format_tasks_briefly(tasks[:15] if isinstance(tasks, list) else [])}

STATUS NOTES
------------
{self._format_all_notes(all_notes[:30])}

KEY INSIGHTS
------------
1. Your productivity peaks on {most_productive_day[0]}, consider scheduling important tasks on this day
2. Focus on reducing pending tasks ({pending_tasks}) to improve completion rate
3. Monitor overdue tasks ({overdue_tasks}) to prevent further delays
4. Your average completion time of {avg_completion_time} hours suggests good time management

RECOMMENDATIONS
---------------
• Schedule challenging tasks on your most productive day ({most_productive_day[0]})
• Set aside dedicated time each day to address pending tasks
• Implement a system to track and reduce overdue tasks
• Consider delegating or breaking down tasks that take longer than average
• Plan next week's tasks in advance to maintain consistent productivity
        """.strip()
    
    def _generate_monthly_summary(self, user_data: Dict, stats: Dict, tasks: List[Dict]) -> str:
        """Generate a monthly summary using AI logic"""
        # Use LLM if available
        if self.llm_provider:
            try:
                # Safely access user data
                user_name = user_data.get('name', 'User') if isinstance(user_data, dict) else 'User'
                user_role = user_data.get('role', 'N/A') if isinstance(user_data, dict) else 'N/A'
                
                # Enhanced prompt with more context and structured analysis
                prompt = f"""
                As an AI Productivity Strategist, generate a comprehensive monthly productivity review for {user_name}, who works as a {user_role}.
                
                USER PROFILE:
                Name: {user_name}
                Role: {user_role}
                
                MONTHLY PERFORMANCE OVERVIEW:
                - Total Tasks Managed: {stats.get('total_tasks', 0) if isinstance(stats, dict) else 0}
                - Tasks Completed: {stats.get('completed_tasks', 0) if isinstance(stats, dict) else 0}
                - Completion Rate: {stats.get('completion_rate', 0) if isinstance(stats, dict) else 0}%
                - Status Distribution: {stats.get('status_distribution', {}) if isinstance(stats, dict) else {}}
                - Status Updates: {stats.get('status_changes', 0) if isinstance(stats, dict) else 0}
                - Average Completion Time: {stats.get('avg_completion_time_hours', 0) if isinstance(stats, dict) else 0} hours
                
                PRODUCTIVITY TREND ANALYSIS:
                - Most Productive Day: {stats.get('most_productive_day', ('N/A', 0))[0] if isinstance(stats, dict) and isinstance(stats.get('most_productive_day'), tuple) else 'N/A'} ({stats.get('most_productive_day', ('N/A', 0))[1] if isinstance(stats, dict) and isinstance(stats.get('most_productive_day'), tuple) else '0'} tasks)
                - Least Productive Day: {stats.get('least_productive_day', ('N/A', 0))[0] if isinstance(stats, dict) and isinstance(stats.get('least_productive_day'), tuple) else 'N/A'} ({stats.get('least_productive_day', ('N/A', 0))[1] if isinstance(stats, dict) and isinstance(stats.get('least_productive_day'), tuple) else '0'} tasks)
                - Average Daily Task Load: {stats.get('avg_tasks_per_day', 0) if isinstance(stats, dict) else 0:.1f} tasks
                
                NOTABLE MONTHLY ACHIEVEMENTS:
                {self._format_tasks_briefly(tasks[:20] if isinstance(tasks, list) else [])}
                
                CRITICAL INSIGHTS FROM STATUS NOTES:
                {self._format_all_notes(stats.get('all_notes', [])[:50] if isinstance(stats, dict) else [])}
                
                INSTRUCTIONS:
                1. Provide a professional executive summary (4-5 sentences) highlighting this month's key achievements and overall productivity trends
                2. Analyze monthly productivity patterns and identify consistent high-performance and low-performance periods
                3. Offer 5 specific, strategic recommendations for next month based on this month's performance
                4. Identify skill development opportunities based on task types and challenges encountered
                5. Predict potential challenges for next month based on unfinished tasks and patterns
                6. Suggest quarterly goals that align with the user's role and long-term objectives
                7. Include a comprehensive SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) based on the month's data
                8. Recommend process improvements to enhance productivity and efficiency
                9. Use a professional, strategic tone with insights tailored to the user's role
                10. Format the response with clear sections: Executive Summary, Monthly Analysis, Strategic Recommendations, Quarterly Goals, SWOT Analysis, Process Improvements
                """
                
                response = self.llm_provider.generate_text(prompt, max_output_tokens=2500, temperature=0.7)
                if response:
                    return response
            except Exception as e:
                print(f"Error generating summary with LLM: {e}")
        
        # Fallback to template-based summary
        # Safely access user data
        user_name = user_data.get('name', 'User') if isinstance(user_data, dict) else 'User'
        user_email = user_data.get('email', 'user@example.com') if isinstance(user_data, dict) else 'user@example.com'
        user_role = user_data.get('role', 'N/A') if isinstance(user_data, dict) else 'N/A'
        
        # Safely access stats data
        total_tasks = stats.get('total_tasks', 0) if isinstance(stats, dict) else 0
        completed_tasks = stats.get('completed_tasks', 0) if isinstance(stats, dict) else 0
        in_progress_tasks = stats.get('in_progress_tasks', 0) if isinstance(stats, dict) else 0
        pending_tasks = stats.get('pending_tasks', 0) if isinstance(stats, dict) else 0
        overdue_tasks = stats.get('overdue_tasks', 0) if isinstance(stats, dict) else 0
        completion_rate = stats.get('completion_rate', 0) if isinstance(stats, dict) else 0
        status_distribution = stats.get('status_distribution', {}) if isinstance(stats, dict) else {}
        status_changes = stats.get('status_changes', 0) if isinstance(stats, dict) else 0
        avg_completion_time = stats.get('avg_completion_time_hours', 0) if isinstance(stats, dict) else 0
        most_productive_day = stats.get('most_productive_day', ('N/A', 0)) if isinstance(stats, dict) else ('N/A', 0)
        least_productive_day = stats.get('least_productive_day', ('N/A', 0)) if isinstance(stats, dict) else ('N/A', 0)
        avg_tasks_per_day = stats.get('avg_tasks_per_day', 0) if isinstance(stats, dict) else 0
        all_notes = stats.get('all_notes', []) if isinstance(stats, dict) else []
        
        return f"""
MONTHLY PRODUCTIVITY REPORT
===========================

Prepared for: {user_name} ({user_email})
Role: {user_role}
Period: Last 30 Days
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
-----------------
Over the past month, you managed {total_tasks} tasks with {completed_tasks} completed, 
achieving a {completion_rate}% completion rate. With {status_changes} status updates 
and an average completion time of {avg_completion_time} hours, your productivity has 
been consistent throughout the month.

MONTHLY ANALYSIS
----------------
• Most Productive Day: {most_productive_day[0]} ({most_productive_day[1]} tasks)
• Least Productive Day: {least_productive_day[0]} ({least_productive_day[1]} tasks)
• Average Daily Task Load: {avg_tasks_per_day} tasks
• In Progress: {in_progress_tasks}
• Pending: {pending_tasks}
• Overdue: {overdue_tasks}

NOTABLE ACHIEVEMENTS
--------------------
{self._format_tasks_briefly(tasks[:20] if isinstance(tasks, list) else [])}

STATUS NOTES
------------
{self._format_all_notes(all_notes[:50])}

SWOT ANALYSIS
-------------
Strengths:
• Consistent daily task management with an average of {avg_tasks_per_day} tasks per day
• Strong completion rate of {completion_rate}%
• Effective time management with average completion time of {avg_completion_time} hours

Weaknesses:
• {pending_tasks} pending tasks that need attention
• {overdue_tasks} overdue tasks that require immediate action
• Inconsistent productivity on {least_productive_day[0]}

Opportunities:
• Leverage peak productivity on {most_productive_day[0]} for challenging tasks
• Implement systems to reduce pending and overdue tasks
• Develop skills in areas where tasks take longer than average

Threats:
• Accumulation of pending tasks may impact future productivity
• Overdue tasks may create additional stress and pressure
• Inconsistent daily productivity may affect long-term goals

STRATEGIC RECOMMENDATIONS
-------------------------
1. Schedule your most challenging tasks on {most_productive_day[0]} to maximize efficiency
2. Implement a daily review system to prevent tasks from becoming overdue
3. Dedicate 30 minutes each day to address pending tasks
4. Analyze tasks with longer completion times to identify improvement opportunities
5. Set weekly mini-goals to maintain consistent progress toward monthly objectives

QUARTERLY GOALS
---------------
• Increase completion rate to 85% or higher
• Reduce pending tasks to under 5 at any given time
• Eliminate overdue tasks entirely
• Improve average completion time by 15%
• Complete at least 90% of tasks before their deadline
        """.strip()
    
    def _generate_custom_summary(self, user_data: Dict, tasks: List[Dict], parameters: Dict[str, Any]) -> str:
        """Generate a custom summary using AI logic"""
        # Use LLM if available
        if self.llm_provider:
            try:
                # Safely access user data
                user_name = user_data.get('name', 'User') if isinstance(user_data, dict) else 'User'
                user_role = user_data.get('role', 'N/A') if isinstance(user_data, dict) else 'N/A'
                
                # Enhanced prompt with more context and structured analysis
                prompt = f"""
                As an AI Productivity Analyst, generate a custom productivity report for {user_name}, who works as a {user_role}.
                
                USER PROFILE:
                Name: {user_name}
                Role: {user_role}
                
                CUSTOM REPORT PARAMETERS:
                {json.dumps(parameters, indent=2)}
                
                IDENTIFIED TASKS:
                {self._format_tasks_briefly(tasks[:20] if isinstance(tasks, list) else [])}
                
                INSTRUCTIONS:
                1. Provide a professional executive summary (3-4 sentences) highlighting key findings based on the custom parameters
                2. Analyze the tasks according to the specified parameters
                3. Offer specific, actionable recommendations based on the custom analysis
                4. Identify patterns or trends in the filtered task set
                5. Suggest improvements or next steps based on the custom parameters
                6. Use a professional, analytical tone with insights tailored to the custom parameters
                7. Format the response with clear sections: Executive Summary, Parameter Analysis, Recommendations, Next Steps
                """
                
                response = self.llm_provider.generate_text(prompt, max_output_tokens=2000, temperature=0.7)
                if response:
                    return response
            except Exception as e:
                print(f"Error generating summary with LLM: {e}")
        
        # Fallback to template-based summary
        # Safely access user data
        user_name = user_data.get('name', 'User') if isinstance(user_data, dict) else 'User'
        user_email = user_data.get('email', 'user@example.com') if isinstance(user_data, dict) else 'user@example.com'
        user_role = user_data.get('role', 'N/A') if isinstance(user_data, dict) else 'N/A'
        
        return f"""
CUSTOM PRODUCTIVITY REPORT
==========================

Prepared for: {user_name} ({user_email})
Role: {user_role}
Parameters: {json.dumps(parameters, indent=2)}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
-----------------
This custom report analyzes your tasks based on the specified parameters. 
The analysis covers {len(tasks)} tasks that match your criteria.

PARAMETER ANALYSIS
------------------
Based on your custom parameters, the following tasks were identified:
{self._format_tasks_briefly(tasks[:20] if isinstance(tasks, list) else [])}

KEY INSIGHTS
------------
1. Custom parameter analysis reveals unique productivity patterns
2. Filtered task set shows specific areas requiring attention
3. Opportunity for targeted skill development in identified areas

RECOMMENDATIONS
---------------
• Review the filtered task set to identify common characteristics
• Implement strategies specific to the tasks matching your parameters
• Set goals based on the patterns identified in this custom analysis
• Consider adjusting parameters for future custom reports to gain deeper insights
        """.strip()
    
    def _format_tasks_briefly(self, tasks: List[Dict]) -> str:
        """Format tasks for brief display in summaries"""
        if not tasks:
            return "No tasks found."
        
        formatted_tasks = []
        for i, task in enumerate(tasks[:10], 1):  # Limit to first 10 tasks
            if isinstance(task, dict):
                title = task.get('title', 'Untitled Task')
                status = task.get('status', 'Unknown')
                formatted_tasks.append(f"{i}. {title} [{status}]")
            else:
                formatted_tasks.append(f"{i}. Unknown Task Format")
        
        return "\n".join(formatted_tasks)
    
    def _format_all_notes(self, notes: List[Dict]) -> str:
        """Format all status notes for display in summaries"""
        if not notes:
            return "No status notes available."
        
        formatted_notes = []
        for i, note in enumerate(notes[:10], 1):  # Limit to first 10 notes
            if isinstance(note, dict):
                status = note.get('status', 'Unknown')
                note_text = note.get('note', 'No note provided')
                updated_at = note.get('updated_at', 'Unknown date')
                # Extract just the date part
                if updated_at and 'T' in updated_at:
                    updated_at = updated_at.split('T')[0]
                formatted_notes.append(f"{i}. [{status}] {updated_at}: {note_text}")
            else:
                formatted_notes.append(f"{i}. Unknown Note Format")
        
        return "\n".join(formatted_notes)