import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
sys.path.append('..')
from database import DatabaseManager
import os

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Cybersecurity Dashboard", page_icon="🔐", layout="wide")

# Check login
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.stop()

st.title("🔐 Cybersecurity Dashboard")
st.markdown("### Incident Response & Threat Analysis")

# Initialize database
db = DatabaseManager()

# Fetch all incidents
df_incidents = db.get_all_incidents()

if df_incidents.empty:
    st.warning("No incident data available")
    st.stop()

# Convert date columns if they exist
if 'reported_date' in df_incidents.columns:
    df_incidents['reported_date'] = pd.to_datetime(df_incidents['reported_date'])
if 'resolved_date' in df_incidents.columns:
    df_incidents['resolved_date'] = pd.to_datetime(df_incidents['resolved_date'])

# Calculate resolution time if both dates exist
if 'reported_date' in df_incidents.columns and 'resolved_date' in df_incidents.columns:
    df_incidents['resolution_time_days'] = (
        df_incidents['resolved_date'] - df_incidents['reported_date']
    ).dt.days

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_incidents = len(df_incidents)
    st.metric("Total Incidents", total_incidents)

with col2:
    unresolved = len(df_incidents[df_incidents['status'] != 'Resolved'])
    st.metric("Unresolved", unresolved, delta=f"{unresolved} pending")

with col3:
    high_severity = len(df_incidents[df_incidents['severity'] == 'High'])
    st.metric("High Severity", high_severity, delta="⚠️ Critical" if high_severity > 5 else "✓ Normal")

with col4:
    if 'resolution_time_days' in df_incidents.columns:
        avg_resolution = df_incidents['resolution_time_days'].mean()
        st.metric("Avg Resolution Time", f"{avg_resolution:.1f} days")
    else:
        st.metric("Avg Resolution Time", "N/A")

st.divider()

st.subheader("🎯 Critical Insight: Phishing Incident Bottleneck Analysis")

# Analysis tabs
tab1, tab2, tab3 = st.tabs(["📊 Resolution Time Analysis", "📈 Incident Trends", "🚨 Critical Cases"])

with tab1:
    st.markdown("### Average Resolution Time by Incident Type")
    
    if 'resolution_time_days' in df_incidents.columns and 'incident_type' in df_incidents.columns:
        # Calculate average resolution time by incident type
        resolution_by_type = df_incidents.groupby('incident_type')['resolution_time_days'].agg(['mean', 'count']).reset_index()
        resolution_by_type.columns = ['Incident Type', 'Avg Days to Resolve', 'Count']
        resolution_by_type = resolution_by_type.sort_values('Avg Days to Resolve', ascending=False)
        
        # Create bar chart
        fig = px.bar(
            resolution_by_type,
            x='Incident Type',
            y='Avg Days to Resolve',
            color='Avg Days to Resolve',
            color_continuous_scale='Reds',
            title='Average Resolution Time by Threat Category',
            text='Avg Days to Resolve'
        )
        fig.update_traces(texttemplate='%{text:.1f} days', textposition='outside')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Key Finding
        slowest_type = resolution_by_type.iloc[0]
        st.warning(f"""
        **🔍 KEY FINDING:** {slowest_type['Incident Type']} incidents take the longest to resolve 
        ({slowest_type['Avg Days to Resolve']:.1f} days on average) with {int(slowest_type['Count'])} cases in the system.
        This represents the primary bottleneck in incident response.
        """)
        
        # Display data table
        st.dataframe(resolution_by_type, use_container_width=True)
    else:
        st.info("Resolution time data not available")

with tab2:
    st.markdown("### Incident Volume Over Time")
    
    if 'reported_date' in df_incidents.columns:
        # Time series of incidents
        incidents_over_time = df_incidents.groupby(df_incidents['reported_date'].dt.date).size().reset_index()
        incidents_over_time.columns = ['Date', 'Count']
        
        fig = px.line(
            incidents_over_time,
            x='Date',
            y='Count',
            title='Daily Incident Reports',
            markers=True
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Breakdown by type
        if 'incident_type' in df_incidents.columns:
            st.markdown("### Incident Distribution by Type")
            type_counts = df_incidents['incident_type'].value_counts().reset_index()
            type_counts.columns = ['Incident Type', 'Count']
            
            fig = px.pie(
                type_counts,
                values='Count',
                names='Incident Type',
                title='Incident Type Distribution',
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### High-Severity Unresolved Incidents")
    
    # Filter high-severity unresolved incidents
    critical_incidents = df_incidents[
        (df_incidents['severity'] == 'High') & 
        (df_incidents['status'] != 'Resolved')
    ]
    
    if not critical_incidents.empty:
        st.error(f"⚠️ {len(critical_incidents)} high-severity incidents require immediate attention!")
        
        # Display critical incidents
        display_cols = ['incident_id', 'incident_type', 'severity', 'status', 'reported_date', 'description']
        available_cols = [col for col in display_cols if col in critical_incidents.columns]
        st.dataframe(
            critical_incidents[available_cols].sort_values('reported_date', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ No high-severity unresolved incidents")

st.divider()


st.subheader("💡 Actionable Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Immediate Actions:
    1. **Prioritize Phishing Response**: Allocate additional resources to phishing incident handling
    2. **Implement Automation**: Deploy automated phishing detection and triage systems
    3. **Staff Training**: Conduct specialized training for phishing incident response
    4. **Escalation Protocol**: Create fast-track escalation for high-severity phishing cases
    """)

with col2:
    st.markdown("""
    #### Long-term Strategies:
    1. **Prevention Focus**: Implement company-wide phishing awareness training
    2. **Tool Investment**: Invest in advanced email filtering and threat detection
    3. **Process Review**: Audit and streamline the incident response workflow
    4. **Metrics Tracking**: Establish KPIs for incident resolution times
    """)

st.divider()

st.subheader("🤖 AI Security Advisor")

with st.expander("Get AI-Powered Security Insights"):
    user_question = st.text_area(
        "Ask the AI about security recommendations, threat analysis, or best practices:",
        placeholder="E.g., 'What are the best practices for handling phishing incidents?'"
    )
    
    if st.button("Get AI Advice"):
        if user_question:
            # Check for OpenAI API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                st.warning("""
                ⚠️ OpenAI API key not configured. To enable AI features:
                1. Set environment variable: `export OPENAI_API_KEY='your-key'`
                2. Or create a `.env` file with: `OPENAI_API_KEY=your-key`
                """)
            else:
                try:
                    import openai
                    openai.api_key = api_key
                    
                    # Prepare context from data
                    context = f"""
                    Current Cybersecurity Metrics:
                    - Total Incidents: {total_incidents}
                    - Unresolved: {unresolved}
                    - High Severity: {high_severity}
                    """
                    
                    # Call OpenAI API
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a cybersecurity expert advisor providing actionable insights."},
                            {"role": "user", "content": f"{context}\n\nQuestion: {user_question}"}
                        ]
                    )
                    
                    st.success("AI Response:")
                    st.write(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"AI service error: {str(e)}")
        else:
            st.warning("Please enter a question")


with st.expander("➕ Add New Incident"):
    with st.form("add_incident_form"):
        new_type = st.selectbox("Incident Type", ["Phishing", "Malware", "DDoS", "Data Breach", "Unauthorized Access"])
        new_severity = st.selectbox("Severity", ["Low", "Medium", "High"])
        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        new_description = st.text_area("Description")
        
        if st.form_submit_button("Add Incident"):
            db.add_incident(new_type, new_severity, new_status, new_description)
            st.success("Incident added successfully!")
            st.rerun()

