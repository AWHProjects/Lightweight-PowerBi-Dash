"""
n8n Workflow Integration Module
Provides automated workflow capabilities for the IT Support Dashboard
"""

import requests
import json
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional

class N8nIntegration:
    def __init__(self, n8n_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        """
        Initialize n8n integration
        
        Args:
            n8n_url: Base URL of n8n instance
            api_key: API key for authentication (if required)
        """
        self.n8n_url = n8n_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def trigger_workflow(self, workflow_name: str, data: Dict) -> Dict:
        """
        Trigger an n8n workflow with data
        
        Args:
            workflow_name: Name of the workflow to trigger
            data: Data to send to the workflow
            
        Returns:
            Response from n8n
        """
        try:
            url = f"{self.n8n_url}/webhook/{workflow_name}"
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'message': 'Workflow triggered successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'message': 'Failed to trigger workflow'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Connection error to n8n'
            }
    
    def setup_sla_monitoring(self, df: pd.DataFrame) -> Dict:
        """
        Set up SLA breach monitoring workflow
        
        Args:
            df: Ticket dataframe
            
        Returns:
            Setup result
        """
        # Find tickets approaching SLA breach
        current_time = datetime.now()
        sla_warnings = []
        
        for _, ticket in df.iterrows():
            if ticket['status'] in ['Open', 'In Progress', 'Pending']:
                hours_elapsed = (current_time - pd.to_datetime(ticket['created_date'])).total_seconds() / 3600
                sla_target = ticket['sla_target_hours']
                
                # Alert if 80% of SLA time has passed
                if hours_elapsed >= (sla_target * 0.8):
                    sla_warnings.append({
                        'ticket_id': ticket['ticket_id'],
                        'title': ticket['title'],
                        'priority': ticket['priority'],
                        'department': ticket['department'],
                        'hours_elapsed': round(hours_elapsed, 1),
                        'sla_target': sla_target,
                        'time_remaining': round(sla_target - hours_elapsed, 1),
                        'assignee': ticket['assignee']
                    })
        
        if sla_warnings:
            return self.trigger_workflow('sla-breach-alert', {
                'alerts': sla_warnings,
                'timestamp': current_time.isoformat(),
                'total_warnings': len(sla_warnings)
            })
        
        return {'success': True, 'message': 'No SLA warnings at this time'}
    
    def generate_weekly_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate and send weekly report via n8n
        
        Args:
            df: Ticket dataframe
            
        Returns:
            Report generation result
        """
        # Calculate weekly metrics
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        weekly_df = df[
            (pd.to_datetime(df['created_date']) >= start_date) &
            (pd.to_datetime(df['created_date']) <= end_date)
        ]
        
        report_data = {
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            },
            'metrics': {
                'total_tickets': len(weekly_df),
                'resolved_tickets': len(weekly_df[weekly_df['status'] == 'Resolved']),
                'sla_compliance': round((weekly_df['sla_met'].sum() / len(weekly_df) * 100) if len(weekly_df) > 0 else 0, 1),
                'avg_resolution_time': round(weekly_df['resolution_hours'].mean() if 'resolution_hours' in weekly_df.columns else 0, 1)
            },
            'by_priority': weekly_df['priority'].value_counts().to_dict(),
            'by_department': weekly_df['department'].value_counts().to_dict(),
            'by_category': weekly_df['category'].value_counts().to_dict()
        }
        
        return self.trigger_workflow('weekly-report', report_data)
    
    def escalate_critical_tickets(self, df: pd.DataFrame) -> Dict:
        """
        Escalate critical tickets that are overdue
        
        Args:
            df: Ticket dataframe
            
        Returns:
            Escalation result
        """
        current_time = datetime.now()
        critical_overdue = []
        
        for _, ticket in df.iterrows():
            if (ticket['priority'] == 'Critical' and 
                ticket['status'] in ['Open', 'In Progress'] and
                not ticket['sla_met']):
                
                hours_elapsed = (current_time - pd.to_datetime(ticket['created_date'])).total_seconds() / 3600
                
                critical_overdue.append({
                    'ticket_id': ticket['ticket_id'],
                    'title': ticket['title'],
                    'department': ticket['department'],
                    'assignee': ticket['assignee'],
                    'hours_overdue': round(hours_elapsed - ticket['sla_target_hours'], 1),
                    'requester': ticket['requester']
                })
        
        if critical_overdue:
            return self.trigger_workflow('critical-escalation', {
                'tickets': critical_overdue,
                'timestamp': current_time.isoformat(),
                'count': len(critical_overdue)
            })
        
        return {'success': True, 'message': 'No critical tickets require escalation'}
    
    def send_slack_notification(self, message: str, channel: str = '#it-support') -> Dict:
        """
        Send notification to Slack via n8n
        
        Args:
            message: Message to send
            channel: Slack channel
            
        Returns:
            Notification result
        """
        return self.trigger_workflow('slack-notification', {
            'message': message,
            'channel': channel,
            'timestamp': datetime.now().isoformat()
        })
    
    def create_jira_ticket(self, ticket_data: Dict) -> Dict:
        """
        Create JIRA ticket for high-priority issues via n8n
        
        Args:
            ticket_data: Ticket information
            
        Returns:
            JIRA creation result
        """
        return self.trigger_workflow('create-jira-ticket', ticket_data)
    
    def get_workflow_status(self, execution_id: str) -> Dict:
        """
        Get status of a workflow execution
        
        Args:
            execution_id: Execution ID from n8n
            
        Returns:
            Execution status
        """
        try:
            url = f"{self.n8n_url}/api/v1/executions/{execution_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def setup_automated_workflows(self, df: pd.DataFrame) -> Dict:
        """
        Set up all automated workflows
        
        Args:
            df: Ticket dataframe
            
        Returns:
            Setup results
        """
        results = {
            'sla_monitoring': self.setup_sla_monitoring(df),
            'critical_escalation': self.escalate_critical_tickets(df),
            'weekly_report': {'success': True, 'message': 'Weekly report scheduled'}
        }
        
        return results

# Example n8n workflow configurations
N8N_WORKFLOWS = {
    'sla-breach-alert': {
        'description': 'Monitors SLA breaches and sends alerts',
        'triggers': ['webhook'],
        'actions': ['email', 'slack', 'teams']
    },
    'weekly-report': {
        'description': 'Generates and distributes weekly reports',
        'triggers': ['schedule', 'webhook'],
        'actions': ['email', 'pdf-generation', 'file-storage']
    },
    'critical-escalation': {
        'description': 'Escalates critical tickets to management',
        'triggers': ['webhook'],
        'actions': ['email', 'sms', 'jira', 'slack']
    },
    'slack-notification': {
        'description': 'Sends notifications to Slack channels',
        'triggers': ['webhook'],
        'actions': ['slack-message']
    },
    'create-jira-ticket': {
        'description': 'Creates JIRA tickets for complex issues',
        'triggers': ['webhook'],
        'actions': ['jira-create', 'email-notification']
    }
}

def get_n8n_integration_status() -> Dict:
    """
    Check if n8n integration is available
    
    Returns:
        Integration status
    """
    try:
        n8n = N8nIntegration()
        # Try to ping n8n instance with shorter timeout
        response = requests.get(f"{n8n.n8n_url}/healthz", timeout=2)
        return {
            'available': response.status_code == 200,
            'url': n8n.n8n_url,
            'workflows': list(N8N_WORKFLOWS.keys()),
            'status': 'connected'
        }
    except requests.exceptions.RequestException as e:
        return {
            'available': False,
            'url': 'http://localhost:5678',
            'workflows': list(N8N_WORKFLOWS.keys()),
            'status': 'disconnected',
            'message': f'n8n instance not accessible: {str(e)[:100]}'
        }
    except Exception as e:
        return {
            'available': False,
            'url': 'http://localhost:5678',
            'workflows': list(N8N_WORKFLOWS.keys()),
            'status': 'error',
            'message': f'Integration error: {str(e)[:100]}'
        }