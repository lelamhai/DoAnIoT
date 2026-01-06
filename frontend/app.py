"""
Streamlit Dashboard - IoT Security Monitoring System
Real-time monitoring với AI predictions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.database import Database
from backend.core.enums import AlertLevel

# Page config
st.set_page_config(
    page_title="IoT Security Monitor",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .safe-status {
        color: #28a745;
        font-weight: bold;
    }
    .warning-status {
        color: #ffc107;
        font-weight: bold;
    }
    .critical-status {
        color: #dc3545;
        font-weight: bold;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize database connection
@st.cache_resource
def get_database():
    """Get database connection"""
    return Database("data/security.db")

db = get_database()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Auto-refresh
    auto_refresh = st.checkbox("Auto Refresh", value=True)
    if auto_refresh:
        refresh_interval = st.slider("Refresh Interval (seconds)", 1, 30, 5)
    
    # Time range filter
    st.markdown("### 📅 Time Range")
    time_range = st.selectbox(
        "Select Range",
        ["Last 1 Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "All Time"]
    )
    
    # Alert filter
    st.markdown("### 🚨 Alert Filter")
    alert_filter = st.multiselect(
        "Show Alerts",
        ["safe", "warning", "critical"],
        default=["safe", "warning", "critical"]
    )
    
    # Statistics
    st.markdown("### 📊 Quick Stats")
    total_events = len(db.get_recent_events(limit=10000))
    st.metric("Total Events", f"{total_events:,}")
    
    # Database info
    st.markdown("### 💾 Database")
    st.info(f"Path: data/security.db")

# Main header
st.markdown('<p class="main-header">🔒 IoT Security Monitoring System</p>', unsafe_allow_html=True)
st.markdown("---")

# Get data
@st.cache_data(ttl=5)
def load_data(time_range_val, alert_filters):
    """Load events from database"""
    # Get recent events
    limit = {
        "Last 1 Hour": 720,      # 1h * 60min * 12 (5s interval)
        "Last 6 Hours": 4320,    # 6h
        "Last 24 Hours": 17280,  # 24h
        "Last 7 Days": 120960,   # 7 days
        "All Time": 100000
    }
    
    events = db.get_recent_events(limit=limit.get(time_range_val, 1000))
    
    if not events:
        return pd.DataFrame()
    
    df = pd.DataFrame(events)
    
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter by alert level
    if alert_filters:
        df = df[df['alert_level'].isin(alert_filters)]
    
    # Filter by time range
    now = pd.Timestamp.now()
    time_delta = {
        "Last 1 Hour": timedelta(hours=1),
        "Last 6 Hours": timedelta(hours=6),
        "Last 24 Hours": timedelta(hours=24),
        "Last 7 Days": timedelta(days=7),
        "All Time": timedelta(days=365)
    }
    
    cutoff = now - time_delta.get(time_range_val, timedelta(hours=24))
    df = df[df['timestamp'] >= cutoff]
    
    return df

df = load_data(time_range, alert_filter)

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

if not df.empty:
    # Current status (latest event)
    latest_event = df.iloc[0]
    latest_alert = latest_event['alert_level'] if 'alert_level' in latest_event else 'safe'
    
    status_icon = {
        'safe': '🟢',
        'warning': '🟡',
        'critical': '🔴'
    }.get(latest_alert, '⚪')
    
    status_text = {
        'safe': 'SAFE',
        'warning': 'WARNING',
        'critical': 'CRITICAL'
    }.get(latest_alert, 'UNKNOWN')
    
    with col1:
        st.metric(
            label="Current Status",
            value=f"{status_icon} {status_text}",
            delta=f"Updated {(datetime.now() - latest_event['timestamp']).seconds}s ago"
        )
    
    # Total events
    with col2:
        motion_count = df[df['motion'] == 1].shape[0]
        st.metric(
            label="Motion Detected",
            value=f"{motion_count:,}",
            delta=f"{motion_count/len(df)*100:.1f}% of events"
        )
    
    # AI predictions
    with col3:
        if 'prediction' in df.columns:
            suspicious_count = df[df['prediction'] == 'suspicious'].shape[0]
            st.metric(
                label="Suspicious Activity",
                value=f"{suspicious_count:,}",
                delta=f"{suspicious_count/len(df)*100:.1f}% of events" if len(df) > 0 else "0%"
            )
        else:
            st.metric(label="AI Predictions", value="N/A")
    
    # Critical alerts
    with col4:
        critical_count = df[df['alert_level'] == 'critical'].shape[0]
        st.metric(
            label="Critical Alerts",
            value=f"{critical_count:,}",
            delta="⚠️ Needs attention" if critical_count > 0 else "✅ All clear"
        )

else:
    st.info("📭 No events in selected time range")

st.markdown("---")

# Charts section
if not df.empty:
    # Timeline chart
    st.subheader("📈 Activity Timeline")
    
    # Prepare data for timeline
    timeline_df = df.copy()
    timeline_df = timeline_df.sort_values('timestamp')
    
    # Create figure
    fig_timeline = go.Figure()
    
    # Add motion line
    fig_timeline.add_trace(go.Scatter(
        x=timeline_df['timestamp'],
        y=timeline_df['motion'],
        mode='lines+markers',
        name='Motion',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    
    # Add alert level colors as background
    if 'alert_level' in timeline_df.columns:
        for alert in ['safe', 'warning', 'critical']:
            alert_data = timeline_df[timeline_df['alert_level'] == alert]
            if not alert_data.empty:
                color_map = {
                    'safe': '#28a745',
                    'warning': '#ffc107',
                    'critical': '#dc3545'
                }
                fig_timeline.add_trace(go.Scatter(
                    x=alert_data['timestamp'],
                    y=alert_data['motion'],
                    mode='markers',
                    name=alert.upper(),
                    marker=dict(
                        color=color_map[alert],
                        size=10,
                        symbol='circle'
                    )
                ))
    
    fig_timeline.update_layout(
        title="Motion Detection Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Motion (0=No, 1=Yes)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Statistics row
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly distribution
        st.subheader("🕐 Hourly Distribution")
        hourly_df = df.copy()
        hourly_df['hour'] = hourly_df['timestamp'].dt.hour
        hourly_counts = hourly_df.groupby('hour').size().reset_index(name='count')
        
        fig_hourly = px.bar(
            hourly_counts,
            x='hour',
            y='count',
            title='Events by Hour of Day',
            labels={'hour': 'Hour', 'count': 'Event Count'}
        )
        fig_hourly.update_layout(height=350)
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        # Alert level distribution
        st.subheader("🚨 Alert Distribution")
        if 'alert_level' in df.columns:
            alert_counts = df['alert_level'].value_counts().reset_index()
            alert_counts.columns = ['alert_level', 'count']
            
            color_map = {
                'safe': '#28a745',
                'warning': '#ffc107',
                'critical': '#dc3545'
            }
            
            fig_alerts = px.pie(
                alert_counts,
                values='count',
                names='alert_level',
                title='Alert Level Distribution',
                color='alert_level',
                color_discrete_map=color_map
            )
            fig_alerts.update_layout(height=350)
            st.plotly_chart(fig_alerts, use_container_width=True)
        else:
            st.info("No alert data available")
    
    st.markdown("---")
    
    # Event log table
    st.subheader("📋 Recent Events")
    
    # Prepare display dataframe
    display_df = df.copy()
    display_df = display_df.sort_values('timestamp', ascending=False)
    
    # Format columns
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df['motion'] = display_df['motion'].apply(lambda x: '🔴 Detected' if x == 1 else '🟢 No Motion')
    
    if 'prediction' in display_df.columns:
        display_df['prediction'] = display_df['prediction'].apply(
            lambda x: '⚠️ SUSPICIOUS' if x == 'suspicious' else '✅ NORMAL' if x == 'normal' else '❓ Unknown'
        )
    
    if 'alert_level' in display_df.columns:
        display_df['alert_level'] = display_df['alert_level'].apply(
            lambda x: '🔴 CRITICAL' if x == 'critical' else '🟡 WARNING' if x == 'warning' else '🟢 SAFE'
        )
    
    # Select columns to display
    display_columns = ['timestamp', 'motion', 'sensor_id', 'location']
    if 'prediction' in display_df.columns:
        display_columns.append('prediction')
    if 'confidence' in display_df.columns:
        display_columns.append('confidence')
    if 'alert_level' in display_df.columns:
        display_columns.append('alert_level')
    
    # Show table
    st.dataframe(
        display_df[display_columns].head(100),
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Events CSV",
        data=csv,
        file_name=f"security_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

else:
    st.warning("No data to display. Please check if backend is running and collecting events.")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**System Status:** 🟢 Online")
with col2:
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with col3:
    st.markdown("**Database:** data/security.db")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
