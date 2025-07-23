import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker()

def generate_ticket_data(num_tickets=1000):
    """Generate realistic IT support ticket data"""
    
    # Define possible values for categorical fields
    priorities = ['Low', 'Medium', 'High', 'Critical']
    priority_weights = [0.4, 0.35, 0.2, 0.05]
    
    statuses = ['Open', 'In Progress', 'Resolved', 'Closed', 'Pending']
    status_weights = [0.15, 0.25, 0.35, 0.20, 0.05]
    
    categories = ['Hardware', 'Software', 'Network', 'Security', 'Access', 'Email', 'Printer', 'Phone']
    category_weights = [0.2, 0.25, 0.15, 0.1, 0.12, 0.08, 0.06, 0.04]
    
    departments = ['IT', 'HR', 'Finance', 'Marketing', 'Sales', 'Operations', 'Legal']
    department_weights = [0.3, 0.15, 0.12, 0.13, 0.15, 0.12, 0.03]
    
    # Generate data
    tickets = []
    
    for i in range(num_tickets):
        # Generate dates (last 6 months)
        created_date = fake.date_time_between(start_date='-6M', end_date='now')
        
        # Priority affects resolution time
        priority = np.random.choice(priorities, p=priority_weights)
        status = np.random.choice(statuses, p=status_weights)
        category = np.random.choice(categories, p=category_weights)
        department = np.random.choice(departments, p=department_weights)
        
        # SLA targets based on priority (in hours)
        sla_targets = {'Low': 72, 'Medium': 24, 'High': 8, 'Critical': 4}
        sla_target = sla_targets[priority]
        
        # Generate resolution time based on priority and some randomness
        if status in ['Resolved', 'Closed']:
            base_resolution_hours = sla_targets[priority]
            # Add some variance - some tickets meet SLA, some don't
            resolution_hours = max(1, np.random.normal(base_resolution_hours * 0.8, base_resolution_hours * 0.4))
            resolved_date = created_date + timedelta(hours=resolution_hours)
            sla_met = resolution_hours <= sla_target
        else:
            resolved_date = None
            # For open tickets, check if they're overdue
            hours_open = (datetime.now() - created_date).total_seconds() / 3600
            sla_met = hours_open <= sla_target
            resolution_hours = None
        
        # Generate assignee
        assignee = fake.name() if status != 'Open' else None
        
        ticket = {
            'ticket_id': f'TKT-{str(i+1).zfill(6)}',
            'title': fake.catch_phrase(),
            'description': fake.text(max_nb_chars=200),
            'priority': priority,
            'status': status,
            'category': category,
            'department': department,
            'requester': fake.name(),
            'assignee': assignee,
            'created_date': created_date,
            'resolved_date': resolved_date,
            'sla_target_hours': sla_target,
            'resolution_hours': resolution_hours,
            'sla_met': sla_met,
            'customer_satisfaction': np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.1, 0.2, 0.4, 0.25]) if status == 'Closed' else None
        }
        
        tickets.append(ticket)
    
    df = pd.DataFrame(tickets)
    return df

def save_sample_data():
    """Generate and save sample data to CSV"""
    df = generate_ticket_data(1000)
    df.to_csv('sample_tickets.csv', index=False)
    print(f"Generated {len(df)} sample tickets and saved to sample_tickets.csv")
    return df

if __name__ == '__main__':
    save_sample_data()