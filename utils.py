import streamlit as st
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password length"""
    return len(password) >= 6

def display_message(type, message):
    """Display message with specified type (success, info, warning, error)"""
    if type == "success":
        st.success(message)
    elif type == "info":
        st.info(message)
    elif type == "warning":
        st.warning(message)
    elif type == "error":
        st.error(message)

def format_date(date_str):
    """Format date string for display"""
    if not date_str:
        return "Unknown date"
    
    try:
        # Handle different date formats
        # This is a simple implementation - can be expanded based on actual date formats
        return date_str
    except:
        return date_str
