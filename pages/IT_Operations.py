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

st.set_page_config(page_title="IT Operations Dashboard", page_icon="🛠️", layout="wide")

# Check login
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.stop()

st.title("🛠️ IT Operations Dashboard")
st.markdown("### Service Desk Performance Monitoring")

# Initialize database
db = DatabaseManager()

# Fetch all tickets
df_tickets = db.get_all_tickets()

if df_tickets.empty:
    st.warning("No ticket data available")
    st.stop()

# Convert date columns if they exist
if 'created_date' in df_tickets.columns:
    df_tickets['created_date'] = pd.to_datetime(df_tickets['created_date'])
if 'resolved_date' in df_tickets.columns:
    df_tickets['resolved_date'] = pd.to_datetime(df_tickets['resolved_date'])

# Calculate resolution time
if 'created_date' in df_tickets.columns and 'resolved_date' in df_tickets.columns:
    df_tickets['resolution_time_days'] = (
        df_tickets['resolved_date'] - df_tickets['created_date']
    ).dt.days

# ==================== KEY METRICS ====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_tickets = len(df_tickets)
    st.metric("Total Tickets", total_tickets)

with col2:
    open_tickets = len(df_tickets[df_tickets['status'].isin(['Open', 'In Progress'])])
    st.metric("Open/In Progress", open_tickets)

with col3:
    if 'priority' in df_tickets.columns:
        high_priority = len(df_tickets[df_tickets['priority'] == 'High'])
        st.metric("High Priority", high_priority)

with col4:
    if 'resolution_time_days' in df_tickets.columns:
        avg_resolution = df_tickets['resolution_time_days'].mean()
        st.metric("Avg Resolution Time", f"{avg_resolution:.1f} days")

st.divider()

# ==================== HIGH-VALUE ANALYSIS ====================
st.subheader("🎯 Critical Insight: Performance Bottleneck Analysis")

tab1, tab2 = st.tabs(["👥 Staff Performance", "⏱️ Status Impact"])

with tab1:
    st.markdown("### Resolution Time by Assigned Staff")
    
    if 'resolution_time_days' in df_tickets.columns and 'assigned_to' in df_tickets.columns:
        # Calculate average resolution time by staff
        staff_performance = df_tickets.groupby('assigned_to').agg({
            'resolution_time_days': 'mean',
            'ticket_id': 'count'
        }).reset_index()
        staff_performance.columns = ['Staff Member', 'Avg Resolution Days', 'Ticket Count']
        staff_performance = staff_performance.sort_values('Avg Resolution Days', ascending=False)
        
        # Create bar chart
        fig = px.bar(
            staff_performance,
            x='Staff Member',
            y='Avg Resolution Days',
            color='Avg Resolution Days',
            color_continuous_scale='Reds',
            title='Average Resolution Time by Staff Member',
            text='Avg Resolution Days',
            hover_data=['Ticket Count']
        )
        fig.update_traces(texttemplate='%{text:.1f} days', textposition='outside')
        fig.update_xaxes(tickangle=-45)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Key Finding
        slowest_staff = staff_performance.iloc[0]
        fastest_staff = staff_performance.iloc[-1]
        difference = slowest_staff['Avg Resolution Days'] - fastest_staff['Avg Resolution Days']
        
        st.warning(f"""
        **🔍 KEY FINDING:** Staff member '{slowest_staff['Staff Member']}' has the longest average 
        resolution time ({slowest_staff['Avg Resolution Days']:.1f} days), which is {difference:.1f} days 
        longer than the fastest staff member. This indicates a performance anomaly requiring investigation.
        """)
        
        st.dataframe(staff_performance, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("### Impact of Ticket Status on Resolution Time")
    
    if 'resolution_time_days' in df_tickets.columns and 'status' in df_tickets.columns:
        # Calculate average resolution time by status
        status_impact = df_tickets.groupby('status').agg({
            'resolution_time_days': 'mean',
            'ticket_id': 'count'
        }).reset_index()
        status_impact.columns = ['Status', 'Avg Resolution Days', 'Count']
        status_impact = status_impact.sort_values('Avg Resolution Days', ascending=False)
        
        # Create bar chart
        fig = px.bar(
            status_impact,
            x='Status',
            y='Avg Resolution Days',
            color='Avg Resolution Days',
            color_continuous_scale='Oranges',
            title='Average Resolution Time by Status',
            text='Avg Resolution Days'
        )
        fig.update_traces(texttemplate='%{text:.1f} days', textposition='outside')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Key Finding
        slowest_status = status_impact.iloc[0]
        st.error(f"""
        **🔍 KEY FINDING:** Tickets in '{slowest_status['Status']}' status have the longest 
        resolution time ({slowest_status['Avg Resolution Days']:.1f} days on average). 
        This process stage represents a critical bottleneck in the workflow.
        """)
        
        st.dataframe(status_impact, use_container_width=True, hide_index=True)

st.divider()

# ==================== ACTIONABLE RECOMMENDATIONS ====================
st.subheader("💡 Performance Optimization Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Immediate Actions:
    1. **Staff Review**: Conduct 1-on-1 with underperforming staff
    2. **Process Audit**: Investigate status bottleneck causes
    3. **Workload Balance**: Redistribute tickets evenly
    4. **Priority Triage**: Implement stricter prioritization
    """)

with col2:
    st.markdown("""
    #### Long-term Strategies:
    1. **Training Program**: Technical training for staff
    2. **Workflow Automation**: Automate ticket routing
    3. **SLA Enforcement**: Establish Service Level Agreements
    4. **Self-Service Portal**: Reduce ticket volume
    """)

st.divider()

# ==================== AI ASSISTANT ====================
st.subheader("🤖 AI Operations Advisor")

with st.expander("Get AI-Powered IT Operations Insights"):
    user_question = st.text_area(
        "Ask about service desk optimization or best practices:",
        placeholder="E.g., 'How can we reduce ticket resolution times?'"
    )
    
    if st.button("Get AI Advice"):
        if user_question:
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                st.warning("⚠️ OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
            else:
                try:
                    import openai
                    openai.api_key = api_key
                    
                    context = f"""
                    Current Metrics:
                    - Total Tickets: {total_tickets}
                    - Open: {open_tickets}
                    - Avg Resolution: {avg_resolution:.1f} days
                    """
                    
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an IT operations expert."},
                            {"role": "user", "content": f"{context}\n\n{user_question}"}
                        ]
                    )
                    
                    st.success("AI Response:")
                    st.write(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"AI service error: {str(e)}")
        else:
            st.warning("Please enter a question")

# ==================== CRUD OPERATIONS ====================
with st.expander("➕ Add New Ticket"):
    with st.form("add_ticket_form"):
        new_title = st.text_input("Ticket Title")
        new_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        new_status = st.selectbox("Status", ["Open", "In Progress", "Waiting for User", "Resolved"])
        new_assigned = st.text_input("Assigned To")
        new_description = st.text_area("Description")
        
        if st.form_submit_button("Add Ticket"):
            if new_title and new_assigned:
                db.add_ticket(new_title, new_priority, new_status, new_assigned, new_description)
                st.success("Ticket added successfully!")
                st.rerun()
            else:
                st.warning("Please provide title and assignee")

with st.expander("🔄 Update Ticket Status"):
    if 'ticket_id' in df_tickets.columns:
        ticket_to_update = st.selectbox(
            "Select ticket",
            options=df_tickets['ticket_id'].tolist(),
            format_func=lambda x: df_tickets[df_tickets['ticket_id']==x]['title'].values[0]
        )
        new_status = st.selectbox("New Status", ["Open", "In Progress", "Waiting for User", "Resolved"], key="update_status")
        
        if st.button("Update Status"):
            db.update_ticket_status(ticket_to_update, new_status)
            st.success("Ticket status updated!")
            st.rerun()