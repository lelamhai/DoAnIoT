"""
FRONTEND - MODULE 3: DASHBOARD ĐƠN GIẢN
Hiển thị dữ liệu từ Database
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.database import Database

# Page config
st.set_page_config(
    page_title="IoT Security Monitor",
    page_icon="🔒",
    layout="wide"
)

# Initialize database
@st.cache_resource
def get_database():
    return Database("data/security.db")

db = get_database()

# Header
st.markdown("# 🔒 IoT Security Monitoring")
st.markdown("---")

# Auto refresh
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

# Refresh button
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button("🔄 Refresh"):
        st.session_state.refresh_count += 1
        st.rerun()
with col2:
    auto_refresh = st.checkbox("Auto (5s)", value=False)

if auto_refresh:
    import time
    time.sleep(5)
    st.rerun()

# Get data
try:
    events = db.get_recent_events(limit=100)
    
    if not events:
        st.warning("⚠️ Chưa có dữ liệu. Chạy Backend trước!")
        st.stop()
    
    df = pd.DataFrame(events)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Statistics
    st.markdown("## 📊 Thống kê")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(df)
        st.metric("Tổng Events", total)
    
    with col2:
        motion_count = df[df['motion'] == 1].shape[0]
        st.metric("Motion Detected", motion_count)
    
    with col3:
        no_motion = df[df['motion'] == 0].shape[0]
        st.metric("No Motion", no_motion)
    
    with col4:
        latest = df.iloc[0]['timestamp']
        st.metric("Latest Event", latest.strftime("%H:%M:%S"))
    
    st.markdown("---")
    
    # Chart
    st.markdown("## 📈 Timeline")
    
    # Prepare chart data
    chart_df = df.copy()
    chart_df['Motion Status'] = chart_df['motion'].map({0: 'No Motion', 1: 'Motion Detected'})
    chart_df['Color'] = chart_df['motion'].map({0: 'green', 1: 'red'})
    
    fig = px.scatter(
        chart_df.tail(50),
        x='timestamp',
        y='motion',
        color='Motion Status',
        color_discrete_map={'No Motion': 'lightgreen', 'Motion Detected': 'red'},
        title='Motion Detection Timeline (Last 50 events)',
        height=400
    )
    
    fig.update_layout(
        yaxis=dict(tickvals=[0, 1], ticktext=['No Motion', 'Motion']),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Events Table
    st.markdown("## 📋 Recent Events")
    
    # Format table
    display_df = df[['timestamp', 'motion', 'sensor_id', 'location']].copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df['motion'] = display_df['motion'].map({0: '⚪ No Motion', 1: '🔴 Motion'})
    display_df = display_df.rename(columns={
        'timestamp': 'Time',
        'motion': 'Status',
        'sensor_id': 'Sensor',
        'location': 'Location'
    })
    
    st.dataframe(
        display_df.head(20),
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    st.markdown("---")
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.info("💡 Tip: Kiểm tra Backend đang chạy và Database có dữ liệu")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    IoT Security Monitoring System v2.0 | Simplified Version
    </div>
    """,
    unsafe_allow_html=True
)
