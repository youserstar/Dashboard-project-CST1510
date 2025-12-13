import streamlit as st
import bcrypt
import sys
sys.path.append('..')
from database import DatabaseManager

st.set_page_config(page_title="Login", page_icon="🔑")

st.title("🔑 Login")

# database initialization
db = DatabaseManager()

# login form
if not st.session_state.get('logged_in', False):
    with st.form("login_form"):
        st.subheader("Enter Your Credentials")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username and password:
                # password has for vertification
                password_bytes = password.encode('utf-8')
                user = db.verify_user(username, password)
                
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user[0]
                    st.session_state.role = user[1]
                    st.success(f"Welcome {username}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    st.divider()
    st.info("""
    **Demo Credentials:**
    - Username: `admin` | Password: `admin123` | Role: Admin
    - Username: `cyber_analyst` | Password: `cyber123` | Role: Cybersecurity
    - Username: `data_scientist` | Password: `data123` | Role: Data Science
    - Username: `it_support` | Password: `it123` | Role: IT Operations
    """)

else:
    st.success(f"Already logged in as: **{st.session_state.username}** ({st.session_state.role})")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()