"""Streamlit dashboard for viewing recognition events."""
import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from face_app.config.settings import DB_PATH


def load_events(limit: int = 100):
    """Load recognition events from database."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        query = f"SELECT id, name, time FROM recognitions ORDER BY id DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


def get_statistics():
    """Get recognition statistics."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM recognitions")
        total = cursor.fetchone()[0]
        
        # Unique people
        cursor.execute("SELECT COUNT(DISTINCT name) FROM recognitions")
        unique_people = cursor.fetchone()[0]
        
        # Today's events
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM recognitions WHERE time LIKE ?", (f"{today}%",))
        today_count = cursor.fetchone()[0]
        
        # Most frequent person
        cursor.execute("""
            SELECT name, COUNT(*) as count 
            FROM recognitions 
            GROUP BY name 
            ORDER BY count DESC 
            LIMIT 1
        """)
        most_frequent = cursor.fetchone()
        
        conn.close()
        
        return {
            "total": total,
            "unique_people": unique_people,
            "today": today_count,
            "most_frequent": most_frequent
        }
    except Exception as e:
        st.error(f"Error getting statistics: {e}")
        return None


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Face Recognition Dashboard",
        page_icon="👤",
        layout="wide"
    )
    
    st.title("👤 Face Recognition Dashboard")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    limit = st.sidebar.slider("Number of records to display", 10, 500, 100)
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=False)
    
    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()
    
    # Statistics
    st.header("📊 Statistics")
    stats = get_statistics()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", stats["total"])
        
        with col2:
            st.metric("Unique People", stats["unique_people"])
        
        with col3:
            st.metric("Today's Events", stats["today"])
        
        with col4:
            if stats["most_frequent"]:
                st.metric("Most Frequent", stats["most_frequent"][0])
                st.caption(f"{stats['most_frequent'][1]} times")
            else:
                st.metric("Most Frequent", "N/A")
    
    st.markdown("---")
    
    # Recent events
    st.header("📝 Recent Recognition Events")
    
    df = load_events(limit)
    
    if not df.empty:
        # Add filtering
        col1, col2 = st.columns(2)
        
        with col1:
            name_filter = st.multiselect(
                "Filter by name",
                options=df['name'].unique().tolist(),
                default=[]
            )
        
        with col2:
            date_filter = st.date_input(
                "Filter by date",
                value=None
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if name_filter:
            filtered_df = filtered_df[filtered_df['name'].isin(name_filter)]
        
        if date_filter:
            date_str = date_filter.strftime("%Y-%m-%d")
            filtered_df = filtered_df[filtered_df['time'].str.startswith(date_str)]
        
        # Display data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"recognition_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Chart
        st.markdown("---")
        st.header("📈 Events by Person")
        
        name_counts = filtered_df['name'].value_counts()
        st.bar_chart(name_counts)
        
    else:
        st.info("📭 No recognition events found. Start the face recognition app to collect data.")
        st.code("python run.py", language="bash")
    
    # Footer
    st.markdown("---")
    st.caption(f"Database: {DB_PATH}")
    st.caption("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()
