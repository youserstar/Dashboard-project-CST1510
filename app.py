import streamlit as st

# page configurations
st.set_page_config(
    page_title="Multi-Domain Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# creating session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None

# main page
st.title("🎯 Multi-Domain Intelligence Platform")

if not st.session_state.logged_in:
    st.info("👈 Please login using the sidebar to access the platform")
    st.markdown("""
    ## Welcome to the Intelligence Platform
    
    This unified platform serves three critical domains:
    
    ### 🔐 Cybersecurity
    - Analyze incident response bottlenecks
    - Track phishing attack trends
    - Identify resolution time issues
    
    ### 📊 Data Science
    - Manage dataset catalog
    - Analyze resource consumption
    - Recommend governance policies
    
    ### 🛠️ IT Operations
    - Monitor service desk performance
    - Identify staff performance patterns
    - Optimize ticket resolution processes
    
    **Please log in to continue →**
    """)
else:
    st.success(f"Welcome back, {st.session_state.username}! ({st.session_state.role})")
    st.markdown("""
    ## Select Your Dashboard
    
    Use the sidebar navigation to access:
    - 🔐 **Cybersecurity Dashboard** - Incident analysis and threat tracking
    - 📊 **Data Science Dashboard** - Dataset management and governance
    - 🛠️ **IT Operations Dashboard** - Service desk performance monitoring
    
    Each dashboard provides real-time insights and AI-powered recommendations.
    """)
    