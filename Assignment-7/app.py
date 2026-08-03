import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai

# Load API Keys
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Life-OS Wellbeing Dashboard", layout="wide")

st.title("🧠 Life-OS: AI Digital Wellbeing Coach")
st.caption("Track daily screen time & get brutal-but-fair productivity coaching.")

# --- Phase 1: Data Pipeline ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("screentime.csv")
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    except Exception as e:
        st.error(f"Error loading screentime.csv: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Please ensure 'screentime.csv' exists in the same folder and has valid data.")
    st.stop()

# --- Phase 2: Sidebar Controls ---
st.sidebar.header("⚙️ Dashboard Controls")

available_dates = df['Date'].unique()
selected_date = st.sidebar.selectbox("Select Date", available_dates, index=len(available_dates)-1)

daily_goal_hours = st.sidebar.slider("Daily Screen Time Goal (Hours)", min_value=1, max_value=12, value=4)
daily_goal_minutes = daily_goal_hours * 60

# Filter Data by Selected Date
day_data = df[df['Date'] == selected_date]

# High-level Metrics
total_minutes_today = int(day_data['Minutes_Used'].sum()) if not day_data.empty else 0
top_app = day_data.loc[day_data['Minutes_Used'].idxmax()]['App_Name'] if not day_data.empty else "N/A"
delta_minutes = total_minutes_today - daily_goal_minutes

# KPI Row
col1, col2, col3 = st.columns(3)
col1.metric("Total Screen Time Today", f"{total_minutes_today // 60}h {total_minutes_today % 60}m")
col2.metric("Most Used App", top_app)
col3.metric(
    "Goal Variance", 
    f"{abs(delta_minutes) // 60}h {abs(delta_minutes) % 60}m", 
    delta=f"{delta_minutes} mins vs limit", 
    delta_color="inverse"
)

st.divider()

# Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📊 Category Breakdown Today")
    cat_summary = day_data.groupby('Category')['Minutes_Used'].sum()
    st.bar_chart(cat_summary)

with col_chart2:
    st.subheader("📈 14-Day Screen Time Trend")
    trend_data = df.groupby('Date')['Minutes_Used'].sum()
    st.line_chart(trend_data)

st.divider()

# --- Phase 3: AI Coaching Integration ---
st.subheader("🤖 Brutal-but-Fair AI Coach Insights")

if st.button("Generate AI Coaching Insights"):
    if not api_key:
        st.error("Gemini API key is missing! Please set GEMINI_API_KEY in your .env file.")
    else:
        summary_str = cat_summary.to_json()
        
        prompt = f"""
        You are a holistic, brutal-but-fair life coach helping software engineers overcome digital addiction.
        
        Screen time breakdown for today (in minutes per category):
        {summary_str}

        Total Time Spent: {total_minutes_today} minutes.
        User's Target Limit: {daily_goal_minutes} minutes.

        Analyze this data and give actionable advice:
        1. Provide a quick, direct assessment of their day without sugarcoating.
        2. Do NOT just say 'use your phone less'. Suggest concrete physical, real-world activity replacements (e.g., fitness, reading, meal prep, outdoor walking) for wasted screen time.
        3. Maintain a motivational yet direct tone.
        """

        with st.spinner("Analyzing habits with Gemini..."):
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )

                if total_minutes_today > daily_goal_minutes:
                    st.warning("⚠️ Screen Time Warning: You exceeded your daily goal!")
                else:
                    st.success("🎉 Great Job! You stayed within your daily screen time goal.")

                st.markdown(response.text)

            except Exception as e:
                st.error(f"Error calling Gemini API: {e}")

# --- Phase 4: Innovation Deliverable (Shareable Link) ---
st.sidebar.divider()
if st.sidebar.button("🔗 Generate Shareable Link"):
    st.query_params["screen_time"] = str(total_minutes_today)
    st.query_params["date"] = str(selected_date)
    st.sidebar.success("URL parameters updated! Copy the browser URL to share.")
