import streamlit as st
from analytics.admin_dashboard import show_admin_analytics

def show_admin_panel():
    """Admin entry point for global system views."""
    from analytics.admin_dashboard import render_admin_dashboard
    render_admin_dashboard()
