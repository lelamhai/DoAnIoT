# Phase 6: Dashboard - COMPLETED ✅

## Tổng quan
Phase 6 đã hoàn thành việc tạo **Streamlit Dashboard** với giao diện web real-time monitoring, hiển thị AI predictions, charts, và event logs.

---

## Dashboard Features

### 1. **Real-time Monitoring** 🔴🟢
- Current system status (SAFE/WARNING/CRITICAL)
- Live motion detection count
- AI suspicious activity tracking
- Critical alerts monitoring
- Auto-refresh every 5 seconds (configurable)

### 2. **Interactive Charts** 📊
- **Activity Timeline**: Motion detection over time với alert level colors
- **Hourly Distribution**: Bar chart showing events by hour of day
- **Alert Distribution**: Pie chart với safe/warning/critical breakdown
- Plotly interactive charts (zoom, pan, hover)

### 3. **Event Log Table** 📋
- Recent 100 events với filtering
- Columns: Timestamp, Motion, Sensor ID, Location, AI Prediction, Confidence, Alert Level
- Color-coded status indicators
- Sortable và searchable
- CSV download functionality

### 4. **Sidebar Controls** ⚙️
- Auto-refresh toggle
- Refresh interval slider (1-30 seconds)
- Time range filter: 1h, 6h, 24h, 7 days, All time
- Alert level filter: safe/warning/critical
- Quick statistics summary
- Database info

### 5. **Responsive Design** 📱
- Wide layout với 4-column metrics
- Custom CSS styling
- Color-coded alerts:
  - 🟢 Green = Safe
  - 🟡 Yellow = Warning
  - 🔴 Red = Critical

---

## Files Created

### Main Dashboard
```
frontend/
├── app.py                    # Main Streamlit application
├── __init__.py               # Package init
└── components/
    └── __init__.py           # Components package
```

### Scripts
```
scripts/
├── demo_dashboard.py         # Generate demo data (288 events)
└── test_live_dashboard.py    # Simulate live events every 5s
```

---

## Usage

### **Step 1: Generate Demo Data**
```bash
python scripts/demo_dashboard.py
```
**Output:**
- 288 events (24 hours of realistic data)
- Patterns: Morning activity, work hours, evening, night
- AI predictions: Normal/Suspicious
- Alert levels: Safe/Warning/Critical

### **Step 2: Run Dashboard**
```bash
streamlit run frontend/app.py
```
**Opens browser at:** http://localhost:8501

### **Step 3: Simulate Live Events (Optional)**
```bash
# Terminal 1: Dashboard (already running)
streamlit run frontend/app.py

# Terminal 2: Live event simulator
python scripts/test_live_dashboard.py
```
**Adds new event every 5 seconds** → Dashboard auto-refreshes

---

## Dashboard Sections

### **Top Metrics (4 cards)**
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Current Status  │ Motion Detected │ Suspicious Act. │ Critical Alerts │
│ 🟢 SAFE         │ 150 (52%)       │ 12 (4%)         │ 3               │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### **Activity Timeline**
- Line chart với motion (0/1)
- Scatter overlay với alert colors
- Hover shows: timestamp, motion, prediction, confidence

### **Hourly Distribution**
- Bar chart: X-axis = hour (0-23), Y-axis = event count
- Shows activity patterns throughout day

### **Alert Distribution**
- Pie chart: Safe vs Warning vs Critical
- Percentage breakdown

### **Event Log Table**
| Timestamp | Motion | Sensor | Location | Prediction | Confidence | Alert |
|-----------|--------|--------|----------|------------|------------|-------|
| 2026-01-06 20:30:00 | 🔴 Detected | PIR_DEMO_01 | living_room | ✅ NORMAL | 0.95 | 🟢 SAFE |
| 2026-01-06 02:15:00 | 🔴 Detected | PIR_DEMO_01 | living_room | ⚠️ SUSPICIOUS | 0.82 | 🔴 CRITICAL |

---

## Configuration Options

### **Sidebar Settings**

**Auto Refresh:**
- ✅ Enabled (default)
- Interval: 1-30 seconds (default: 5s)

**Time Range:**
- Last 1 Hour (720 events)
- Last 6 Hours (4,320 events)
- Last 24 Hours (17,280 events)
- Last 7 Days
- All Time

**Alert Filter:**
- [x] safe
- [x] warning
- [x] critical

---

## Data Flow

```
┌──────────────┐
│   Database   │
│ security.db  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  load_data(time_range, alert_filter) │
│  - Query recent events               │
│  - Filter by time & alert            │
│  - Convert to DataFrame              │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Streamlit UI Rendering              │
│  - Metrics cards                     │
│  - Plotly charts                     │
│  - Event table                       │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Auto-refresh (every 5s)             │
│  st.rerun() → Re-query database      │
└──────────────────────────────────────┘
```

---

## Screenshots Guide

### **Dashboard Layout:**
```
╔════════════════════════════════════════════════════════════════╗
║         🔒 IoT Security Monitoring System                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          ║
║  │ Current  │ │  Motion  │ │Suspicious│ │ Critical │          ║
║  │ Status   │ │ Detected │ │ Activity │ │  Alerts  │          ║
║  │ 🟢 SAFE  │ │   150    │ │    12    │ │    3     │          ║
║  └──────────┘ └──────────┘ └──────────┘ └──────────┘          ║
║                                                                ║
║  ┌──────────────────────────────────────────────────────────┐  ║
║  │         📈 Activity Timeline                            │  ║
║  │  [Line chart with motion over time]                     │  ║
║  └──────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────┐  ┌────────────────────────┐        ║
║  │  🕐 Hourly Distribution│  │ 🚨 Alert Distribution  │        ║
║  │  [Bar chart]           │  │ [Pie chart]            │        ║
║  └────────────────────────┘  └────────────────────────┘        ║
║                                                                ║
║  ┌──────────────────────────────────────────────────────────┐  ║
║  │         📋 Recent Events                                │  ║
║  │  [Event log table with 100 rows]                        │  ║
║  │  📥 Download CSV                                         │  ║
║  └──────────────────────────────────────────────────────────┘  ║
╚════════════════════════════════════════════════════════════════╝
```

---

## Technical Details

### **Dependencies**
```python
streamlit>=1.29.0
plotly>=5.18.0
pandas>=2.1.4
```

### **Caching Strategy**
```python
@st.cache_resource  # Database connection (persistent)
def get_database():
    return Database("data/security.db")

@st.cache_data(ttl=5)  # Data loading (5s TTL)
def load_data(time_range, alert_filters):
    # Query and filter events
    return df
```

### **Performance**
- Cached database connection (singleton)
- Data cached with 5s TTL
- Efficient SQL queries with indexes
- Limit recent events (max 100k)

---

## Integration với Backend

### **Scenario 1: Live Backend**
```bash
# Terminal 1: Backend với AI
python backend/main.py

# Terminal 2: Dashboard
streamlit run frontend/app.py
```
Backend publish events → Database → Dashboard auto-refresh shows new data

### **Scenario 2: Demo Mode**
```bash
# Generate demo data once
python scripts/demo_dashboard.py

# Run dashboard
streamlit run frontend/app.py
```
Static demo data cho presentation

### **Scenario 3: Live Simulation**
```bash
# Terminal 1: Dashboard
streamlit run frontend/app.py

# Terminal 2: Simulator
python scripts/test_live_dashboard.py
```
Simulated events every 5s

---

## Customization

### **Change Refresh Interval**
Dashboard sidebar → Auto Refresh → Adjust slider (1-30s)

### **Change Time Range**
Sidebar → Time Range → Select (1h, 6h, 24h, 7d, All)

### **Filter Alerts**
Sidebar → Alert Filter → Check/uncheck safe/warning/critical

### **Modify Colors**
Edit `frontend/app.py`:
```python
color_map = {
    'safe': '#28a745',     # Green
    'warning': '#ffc107',  # Yellow
    'critical': '#dc3545'  # Red
}
```

---

## Testing Checklist

- [x] Dashboard loads without errors
- [x] Metrics display correctly
- [x] Charts render (timeline, hourly, alerts)
- [x] Event table shows data
- [x] Auto-refresh works
- [x] Time range filter works
- [x] Alert filter works
- [x] CSV download works
- [x] Responsive layout
- [x] Live updates (with backend/simulator)

---

## Known Issues & Fixes

### **Issue 1: "No events in selected time range"**
**Fix:** Run `python scripts/demo_dashboard.py` to generate data

### **Issue 2: Dashboard doesn't auto-refresh**
**Fix:** Check "Auto Refresh" in sidebar, verify interval > 0

### **Issue 3: Charts not rendering**
**Fix:** Ensure `plotly` installed: `pip install plotly`

### **Issue 4: Database locked**
**Fix:** Close other connections, restart dashboard

---

## Demo Scenarios

### **Scenario 1: Morning Activity**
- Time: 7h-9h
- Pattern: High motion (80%)
- AI: NORMAL predictions
- Alert: SAFE

### **Scenario 2: Late Night Intrusion**
- Time: 2h-4h
- Pattern: Motion detected
- AI: SUSPICIOUS (70-95% confidence)
- Alert: CRITICAL

### **Scenario 3: Work Hours Intrusion**
- Time: 9h-17h weekdays
- Pattern: Unexpected motion
- AI: SUSPICIOUS
- Alert: WARNING/CRITICAL

---

## Next Steps

### **Phase 7: Integration**
- Connect dashboard với live backend
- Test full pipeline: ESP32 → MQTT → Backend → AI → Dashboard
- Performance optimization
- Alert notifications

### **Enhancements (Optional)**
- Real-time video feed
- Email/Telegram alerts
- Multi-sensor support
- Historical analytics
- Export reports (PDF)
- User authentication

---

## Summary

✅ **Phase 6 COMPLETED**

**Deliverables:**
- Streamlit dashboard với 5 main sections
- Real-time monitoring với auto-refresh
- Interactive charts (Plotly)
- Event log table với CSV export
- Demo data generator (288 events)
- Live event simulator
- Responsive design với custom CSS

**Access:**
- URL: http://localhost:8501
- Auto-refresh: 5s (configurable)
- Data source: data/security.db

**Ready for:** Phase 7 (Integration & Testing)

---

**Generated:** January 6, 2026  
**Phase Duration:** 1.5 hours  
**Status:** ✅ COMPLETE
