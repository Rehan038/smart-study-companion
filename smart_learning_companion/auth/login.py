import streamlit as st
from database.db import validate_user, register_user

def logout_user():
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""

def show_login_page():
    """Simple and clean Login/Signup UI with a solid background."""
    
    # Minimalist CSS for background color
    st.markdown("""
        <style>
        .stApp {
            background-color: #0f172a;
        }
        .main-title {
            color: white;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 0;
        }
        .sub-title {
            color: #94a3b8;
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="main-title">Study Companion</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Your AI-Powered Learning Hub</p>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    user = validate_user(u, p)
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = user["username"]
                        st.session_state["role"] = user["role"]
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        
        with tab2:
            with st.form("signup"):
                new_u = st.text_input("New Username")
                new_p = st.text_input("New Password", type="password")
                conf_p = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not new_u or not new_p:
                        st.warning("All fields are required.")
                    elif new_p != conf_p:
                        st.error("Passwords do not match.")
                    else:
                        if register_user(new_u, new_p):
                            st.success("Account created! You can now login.")
                        else:
                            st.error("Username already exists.")
