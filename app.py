import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
from n8n_integration import N8nIntegration, get_n8n_integration_status
import json

# Initialize the Dash app with professional styling
app = dash.Dash(__name__,
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP,
                    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
                ],
                assets_folder='assets')
app.title = "IT Support Dashboard - Power BI Clone"

# Initialize n8n integration
n8n = N8nIntegration()
n8n_status = get_n8n_integration_status()

# Load and preprocess data
def load_data():
    """Load and preprocess the ticket data"""
    try:
        df = pd.read_csv('sample_tickets.csv')
        df['created_date'] = pd.to_datetime(df['created_date'])
        df['resolved_date'] = pd.to_datetime(df['resolved_date'])
        
        # Add derived columns for analysis
        df['created_week'] = df['created_date'].dt.isocalendar().week
        df['created_weekday'] = df['created_date'].dt.day_name()
        df['created_month'] = df['created_date'].dt.strftime('%Y-%m')
        df['days_to_resolve'] = (df['resolved_date'] - df['created_date']).dt.days
        
        return df
    except FileNotFoundError:
        # Return empty dataframe if file doesn't exist
        return pd.DataFrame()

# Load data
df = load_data()

# Define color schemes
PRIORITY_COLORS = {
    'Low': '#28a745',
    'Medium': '#ffc107',
    'High': '#fd7e14',
    'Critical': '#dc3545'
}

STATUS_COLORS = {
    'Open': '#dc3545',
    'In Progress': '#ffc107',
    'Resolved': '#28a745',
    'Closed': '#6c757d',
    'Pending': '#17a2b8'
}

# Create KPI cards
def create_kpi_card(title, value, subtitle="", color="primary"):
    return dbc.Card([
        dbc.CardBody([
            html.H4(value, className="card-title text-center", style={'color': f'var(--bs-{color})', 'font-weight': 'bold'}),
            html.P(title, className="card-text text-center text-muted"),
            html.Small(subtitle, className="text-center d-block text-muted")
        ])
    ], className="mb-3")

# Calculate KPIs
if not df.empty:
    total_tickets = len(df)
    open_tickets = len(df[df['status'].isin(['Open', 'In Progress', 'Pending'])])
    sla_compliance = (df['sla_met'].sum() / len(df) * 100) if len(df) > 0 else 0
    avg_resolution_time = df['resolution_hours'].mean() if 'resolution_hours' in df.columns else 0
else:
    total_tickets = 0
    open_tickets = 0
    sla_compliance = 0
    avg_resolution_time = 0

# Dashboard layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("IT Support Dashboard", className="text-center mb-4", style={'color': '#2c3e50'}),
            html.Hr()
        ])
    ]),
    
    # KPI Cards Row
    dbc.Row([
        dbc.Col([
            create_kpi_card("Total Tickets", f"{total_tickets:,}", "All time", "info")
        ], width=3),
        dbc.Col([
            create_kpi_card("Open Tickets", f"{open_tickets:,}", "Active workload", "warning")
        ], width=3),
        dbc.Col([
            create_kpi_card("SLA Compliance", f"{sla_compliance:.1f}%", "Target: 95%", "success" if sla_compliance >= 95 else "danger")
        ], width=3),
        dbc.Col([
            create_kpi_card("Avg Resolution", f"{avg_resolution_time:.1f}h", "Mean time", "primary")
        ], width=3),
    ], className="mb-4"),
    
    # Filters Row
    dbc.Row([
        dbc.Col([
            html.Label("Date Range:", className="fw-bold"),
            dcc.DatePickerRange(
                id='date-range-picker',
                start_date=df['created_date'].min() if not df.empty else datetime.now() - timedelta(days=30),
                end_date=df['created_date'].max() if not df.empty else datetime.now(),
                display_format='YYYY-MM-DD'
            )
        ], width=3),
        dbc.Col([
            html.Label("Priority:", className="fw-bold"),
            dcc.Dropdown(
                id='priority-filter',
                options=[{'label': 'All', 'value': 'all'}] + [{'label': p, 'value': p} for p in df['priority'].unique()] if not df.empty else [],
                value='all',
                clearable=False
            )
        ], width=3),
        dbc.Col([
            html.Label("Department:", className="fw-bold"),
            dcc.Dropdown(
                id='department-filter',
                options=[{'label': 'All', 'value': 'all'}] + [{'label': d, 'value': d} for d in df['department'].unique()] if not df.empty else [],
                value='all',
                clearable=False
            )
        ], width=3),
        dbc.Col([
            html.Label("Status:", className="fw-bold"),
            dcc.Dropdown(
                id='status-filter',
                options=[{'label': 'All', 'value': 'all'}] + [{'label': s, 'value': s} for s in df['status'].unique()] if not df.empty else [],
                value='all',
                clearable=False
            )
        ], width=3),
    ], className="mb-4"),
    
    # Charts Row 1
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='ticket-trends-chart')
        ], width=8),
        dbc.Col([
            dcc.Graph(id='priority-distribution-chart')
        ], width=4),
    ], className="mb-4"),
    
    # Charts Row 2
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='sla-performance-chart')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='department-analysis-chart')
        ], width=6),
    ], className="mb-4"),
    
    # Charts Row 3
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='weekly-trends-chart')
        ], width=8),
        dbc.Col([
            dcc.Graph(id='status-distribution-chart')
        ], width=4),
    ], className="mb-4"),
    
    # Footer
    html.Hr(),
    html.P("IT Support Dashboard - Power BI Clone built with Plotly Dash",
           className="text-center text-muted"),
    
    # Hidden div to store n8n status
    html.Div(id='n8n-status', style={'display': 'none'}, children=json.dumps(n8n_status)),
    
    # Interval component for real-time updates
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # Update every 30 seconds
        n_intervals=0
    )
    
], fluid=True)

# Enhanced chart configurations
def get_enhanced_chart_config():
    """Get enhanced chart configuration for better interactivity"""
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': [
            'drawline',
            'drawopenpath',
            'drawclosedpath',
            'drawcircle',
            'drawrect',
            'eraseshape'
        ],
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'dashboard_chart',
            'height': 500,
            'width': 700,
            'scale': 1
        }
    }

# Add n8n integration callbacks
@app.callback(
    Output('n8n-status', 'children'),
    [Input('interval-component', 'n_intervals')],
    prevent_initial_call=True
)
def update_n8n_status(n):
    """Update n8n integration status"""
    try:
        status = get_n8n_integration_status()
        
        # Only trigger workflows if n8n is available and we have data
        if status.get('available', False) and not df.empty:
            try:
                # Set up SLA monitoring (non-blocking)
                n8n.setup_sla_monitoring(df)
                
                # Check for critical escalations (non-blocking)
                n8n.escalate_critical_tickets(df)
                
            except Exception as workflow_error:
                print(f"n8n workflow error: {workflow_error}")
                status['workflow_error'] = str(workflow_error)
        
        return json.dumps(status)
    except Exception as e:
        print(f"n8n status error: {e}")
        return json.dumps({
            'available': False,
            'error': str(e),
            'workflows': []
        })

# Callback for filtering data
def filter_data(start_date, end_date, priority, department, status):
    """Filter dataframe based on user selections"""
    if df.empty:
        return df
    
    filtered_df = df.copy()
    
    # Date filter
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['created_date'] >= start_date) &
            (filtered_df['created_date'] <= end_date)
        ]
    
    # Priority filter
    if priority != 'all':
        filtered_df = filtered_df[filtered_df['priority'] == priority]
    
    # Department filter
    if department != 'all':
        filtered_df = filtered_df[filtered_df['department'] == department]
    
    # Status filter
    if status != 'all':
        filtered_df = filtered_df[filtered_df['status'] == status]
    
    return filtered_df

# Ticket trends chart callback
@app.callback(
    Output('ticket-trends-chart', 'figure'),
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('priority-filter', 'value'),
     Input('department-filter', 'value'),
     Input('status-filter', 'value')]
)
def update_ticket_trends(start_date, end_date, priority, department, status):
    filtered_df = filter_data(start_date, end_date, priority, department, status)
    
    if filtered_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    # Group by date and count tickets
    daily_tickets = filtered_df.groupby(filtered_df['created_date'].dt.date).size().reset_index()
    daily_tickets.columns = ['date', 'count']
    
    # Also get resolved tickets
    resolved_df = filtered_df[filtered_df['resolved_date'].notna()]
    if not resolved_df.empty:
        daily_resolved = resolved_df.groupby(resolved_df['resolved_date'].dt.date).size().reset_index()
        daily_resolved.columns = ['date', 'resolved_count']
    else:
        daily_resolved = pd.DataFrame(columns=['date', 'resolved_count'])
    
    fig = go.Figure()
    
    # Add created tickets line
    fig.add_trace(go.Scatter(
        x=daily_tickets['date'],
        y=daily_tickets['count'],
        mode='lines+markers',
        name='Tickets Created',
        line=dict(color='#dc3545', width=2),
        marker=dict(size=6)
    ))
    
    # Add resolved tickets line
    if not daily_resolved.empty:
        fig.add_trace(go.Scatter(
            x=daily_resolved['date'],
            y=daily_resolved['resolved_count'],
            mode='lines+markers',
            name='Tickets Resolved',
            line=dict(color='#28a745', width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title={
            'text': 'Ticket Trends Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Segoe UI'}
        },
        xaxis_title='Date',
        yaxis_title='Number of Tickets',
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Segoe UI'},
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # Add range selector
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="7d", step="day", stepmode="backward"),
                    dict(count=30, label="30d", step="day", stepmode="backward"),
                    dict(count=90, label="3m", step="day", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    return fig

# Priority distribution chart callback
@app.callback(
    Output('priority-distribution-chart', 'figure'),
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('priority-filter', 'value'),
     Input('department-filter', 'value'),
     Input('status-filter', 'value')]
)
def update_priority_distribution(start_date, end_date, priority, department, status):
    filtered_df = filter_data(start_date, end_date, priority, department, status)
    
    if filtered_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    priority_counts = filtered_df['priority'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=priority_counts.index,
        values=priority_counts.values,
        marker_colors=[PRIORITY_COLORS.get(p, '#6c757d') for p in priority_counts.index],
        textinfo='label+percent',
        textposition='auto'
    )])
    
    fig.update_layout(
        title={
            'text': 'Priority Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Segoe UI'}
        },
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Segoe UI'},
        showlegend=True,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # Add hover template
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        textfont_size=12
    )
    
    return fig

# SLA performance chart callback
@app.callback(
    Output('sla-performance-chart', 'figure'),
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('priority-filter', 'value'),
     Input('department-filter', 'value'),
     Input('status-filter', 'value')]
)
def update_sla_performance(start_date, end_date, priority, department, status):
    filtered_df = filter_data(start_date, end_date, priority, department, status)
    
    if filtered_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    # Calculate SLA performance by priority
    sla_by_priority = filtered_df.groupby('priority')['sla_met'].agg(['count', 'sum']).reset_index()
    sla_by_priority['sla_percentage'] = (sla_by_priority['sum'] / sla_by_priority['count'] * 100)
    
    fig = go.Figure(data=[go.Bar(
        x=sla_by_priority['priority'],
        y=sla_by_priority['sla_percentage'],
        marker_color=[PRIORITY_COLORS.get(p, '#6c757d') for p in sla_by_priority['priority']],
        text=[f"{p:.1f}%" for p in sla_by_priority['sla_percentage']],
        textposition='auto'
    )])
    
    # Add target line at 95%
    fig.add_hline(y=95, line_dash="dash", line_color="red",
                  annotation_text="Target: 95%")
    
    fig.update_layout(
        title={
            'text': 'SLA Performance by Priority',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Segoe UI'}
        },
        xaxis_title='Priority',
        yaxis_title='SLA Compliance (%)',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Segoe UI'},
        yaxis=dict(range=[0, 100]),
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False
    )
    
    # Add hover template
    fig.update_traces(
        hovertemplate='<b>%{x} Priority</b><br>SLA Compliance: %{y:.1f}%<br>Target: 95%<extra></extra>'
    )
    
    # Add annotations for values below target
    for i, (priority, percentage) in enumerate(zip(sla_by_priority['priority'], sla_by_priority['sla_percentage'])):
        if percentage < 95:
            fig.add_annotation(
                x=priority,
                y=percentage + 5,
                text="⚠️ Below Target",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                font=dict(color="red", size=10)
            )
    
    return fig

# Department analysis chart callback
@app.callback(
    Output('department-analysis-chart', 'figure'),
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('priority-filter', 'value'),
     Input('department-filter', 'value'),
     Input('status-filter', 'value')]
)
def update_department_analysis(start_date, end_date, priority, department, status):
    filtered_df = filter_data(start_date, end_date, priority, department, status)
    
    if filtered_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    dept_counts = filtered_df['department'].value_counts()
    
    fig = go.Figure(data=[go.Bar(
        x=dept_counts.values,
        y=dept_counts.index,
        orientation='h',
        marker_color='#17a2b8',
        text=dept_counts.values,
        textposition='auto'
    )])
    
    fig.update_layout(
        title={
            'text': 'Tickets by Department',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Segoe UI'}
        },
        xaxis_title='Number of Tickets',
        yaxis_title='Department',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Segoe UI'},
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False
    )
    
    # Add hover template
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Tickets: %{x}<extra></extra>',
        marker=dict(
            line=dict(color='rgba(255,255,255,0.8)', width=2),
            color='#17a2b8'
        )
    )
    
    return fig

# Weekly trends chart callback
@app.callback(
    Output('weekly-trends-chart', 'figure'),
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('priority-filter', 'value'),
     Input('department-filter', 'value'),
     Input('status-filter', 'value')]
)
def update_weekly_trends(start_date, end_date, priority, department, status):
    filtered_df = filter_data(start_date, end_date, priority, department, status)
    
    if filtered_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    # Group by weekday
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_counts = filtered_df['created_weekday'].value_counts().reindex(weekday_order, fill_value=0)
    
    fig = go.Figure(data=[go.Bar(
        x=weekday_counts.index,
        y=weekday_counts.values,
        marker_color='#fd7e14',
        text=weekday_counts.values,
        textposition='auto'
    )])
    
    fig.update_layout(
        title={
            'text': 'Weekly Incident Trends',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Segoe UI'}
        },
        xaxis_title='Day of Week',
        yaxis_title='Number of Tickets',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Segoe UI'},
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False
    )
    
    # Add hover template and gradient colors
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Tickets: %{y}<br><extra></extra>',
        marker=dict(
            color=weekday_counts.values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Ticket Count"),
            line=dict(color='rgba(255,255,255,0.8)', width=2)
        )
    )
    
    # Add trend line
    if len(weekday_counts) > 1:
        fig.add_scatter(
            x=weekday_counts.index,
            y=weekday_counts.values,
            mode='lines',
            name='Trend',
            line=dict(color='red', width=3, dash='dash'),
            hovertemplate='Trend Line<extra></extra>'
        )
    
    return fig

# Status distribution chart callback
@app.callback(
    Output('status-distribution-chart', 'figure'),
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('priority-filter', 'value'),
     Input('department-filter', 'value'),
     Input('status-filter', 'value')]
)
def update_status_distribution(start_date, end_date, priority, department, status):
    filtered_df = filter_data(start_date, end_date, priority, department, status)
    
    if filtered_df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    status_counts = filtered_df['status'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        marker_colors=[STATUS_COLORS.get(s, '#6c757d') for s in status_counts.index],
        textinfo='label+percent',
        textposition='auto'
    )])
    
    fig.update_layout(
        title={
            'text': 'Status Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Segoe UI'}
        },
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Segoe UI'},
        showlegend=True,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # Add hover template and enhanced styling
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        textfont_size=12,
        marker=dict(
            line=dict(color='rgba(255,255,255,0.8)', width=2)
        ),
        pull=[0.1 if status == 'Open' else 0 for status in status_counts.index]  # Pull out 'Open' slice
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)