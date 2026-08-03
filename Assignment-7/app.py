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
        # Dynamic File Path Resolution (Fixes Streamlit Cloud missing file error)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(BASE_DIR, "screentime.csv")
        
        df = pd.read_csv(csv_path)
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
st.sidebar.header("Filter Options")

# Date range selection
available_dates = sorted(df['Date'].unique())
min_date = available_dates[0]
max_date = available_dates[-1]

selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle single date vs range selection
if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
else:
    start_date = end_date = selected_date_range

# Category Filter
categories = ["All"] + list(df['Category'].unique())
selected_category = st.sidebar.selectbox("Filter by Category", categories)

# Apply Filters
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

# --- Phase 3: Analytics Dashboard ---
st.header("📊 Screen Time Analytics")

col1, col2, col3 = st.columns(3)

total_minutes = filtered_df['Minutes_Used'].sum()
total_hours = round(total_minutes / 60, 2)
most_used_app = filtered_df.groupby('App_Name')['Minutes_Used'].sum().idxmax() if not filtered_df.empty else "N/A"

col1.metric("Total Screen Time", f"{total_hours} hrs")
col2.metric("Total Minutes", f"{total_minutes} mins")
col3.metric("Most Used App", most_used_app)

st.divider()

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Category Breakdown")
    category_data = filtered_df.groupby('Category')['Minutes_Used'].sum().reset_index()
    st.bar_chart(category_data, x='Category', y='Minutes_Used')

with col_chart2:
    st.subheader("Daily Usage Trend")
    daily_data = filtered_df.groupby('Date')['Minutes_Used'].sum().reset_index()
    st.line_chart(daily_data, x='Date', y='Minutes_Used')

# --- Phase 4: Gemini AI Coaching ---
st.divider()
st.header("🤖 AI Productivity Coach")

if st.button("Generate AI Feedback", type="primary"):
    if not api_key:
        st.error("Gemini API key is missing. Please set GEMINI_API_KEY in Streamlit Secrets.")
    else:
        with st.spinner("Analyzing your digital habits..."):
            try:
                # Prepare summary data for prompt
                app_summary = filtered_df.groupby(['Category', 'App_Name'])['Minutes_Used'].sum().to_string()
                
                prompt = f"""
                You are a witty, direct, and pragmatic AI Digital Wellbeing Coach.
                Analyze the following screen time data for a user:
                
                {app_summary}
                
                Provide a short 3-part response:
                1. 🎯 **The Reality Check**: Highlight where they are wasting time vs doing meaningful work.
                2. 🔥 **The Roast**: Give a lighthearted, humorous roast based on their top distraction app.
                3. 🚀 **Action Plan**: Give 2 specific, actionable rules to improve their digital habits tomorrow.
                """
                
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Failed to generate AI feedback: {e}")
