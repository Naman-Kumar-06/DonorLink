import streamlit as st
import database
from utils import validate_email, validate_password, display_message

def show_auth_page():
    st.title("🩸 Blood Bank Management System")
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_signup_form()

def show_login_form():
    st.header("Login")
    
    # Login form
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        login_button = st.button("Login", use_container_width=True)
    
    if login_button:
        if not email or not password:
            st.error("Please fill in all fields.")
            return
        
        try:
            # Authenticate user with Firebase
            auth = database.get_auth()
            user = auth.sign_in_with_email_and_password(email, password)
            
            # Get user details from Firestore
            db = database.get_firestore_db()
            user_data = db.collection('users').document(user['localId']).get().to_dict()
            
            if not user_data:
                st.error("User profile is incomplete. Please contact administrator.")
                return
            
            # Store user info in session state
            st.session_state.user = user_data
            st.session_state.user_role = user_data.get('role')
            st.session_state.user_id = user['localId']
            st.session_state.logged_in = True
            
            # Refresh page to show dashboard
            st.rerun()
        
        except Exception as e:
            error_message = str(e)
            if "INVALID_EMAIL" in error_message:
                st.error("Invalid email format. Please check and try again.")
            elif "INVALID_PASSWORD" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
                st.error("Incorrect email or password. Please try again.")
            elif "USER_DISABLED" in error_message:
                st.error("This account has been disabled. Please contact the administrator.")
            elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_message:
                st.error("Too many failed login attempts. Please try again later.")
            else:
                st.error(f"Login failed: {error_message}")

def show_signup_form():
    st.header("Sign Up")
    
    # Signup form
    name = st.text_input("Full Name", key="signup_name")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
    
    # Role selection
    role = st.selectbox("Register as", ["donor", "receiver"])
    
    # Additional fields based on role
    if role == "donor":
        blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        phone = st.text_input("Phone Number", key="donor_phone")
        address = st.text_area("Address", key="donor_address")
        city = st.text_input("City", key="donor_city")
        available = st.checkbox("Available for donation", value=True)
    else:  # receiver
        organization = st.text_input("Organization/Hospital Name")
        phone = st.text_input("Phone Number", key="receiver_phone")
        address = st.text_area("Address", key="receiver_address")
        city = st.text_input("City", key="receiver_city")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        signup_button = st.button("Sign Up", use_container_width=True)
    
    if signup_button:
        # Validate form inputs
        if not name or not email or not password or not confirm_password:
            st.error("Please fill in all required fields.")
            return
        
        if not validate_email(email):
            st.error("Please enter a valid email address.")
            return
        
        if not validate_password(password):
            st.error("Password must be at least 6 characters long.")
            return
        
        if password != confirm_password:
            st.error("Passwords do not match.")
            return
        
        if role == "donor" and (not blood_group or not phone or not address or not city):
            st.error("Please fill in all donor information.")
            return
        
        if role == "receiver" and (not organization or not phone or not address or not city):
            st.error("Please fill in all receiver information.")
            return
        
        try:
            # Create user in Firebase Authentication
            auth = database.get_auth()
            user = auth.create_user_with_email_and_password(email, password)
            
            # Prepare user data for Firestore
            user_data = {
                "name": name,
                "email": email,
                "role": role,
                "phone": phone,
                "address": address,
                "city": city,
                "created_at": database.get_server_timestamp()
            }
            
            # Add role-specific data
            if role == "donor":
                user_data.update({
                    "blood_group": blood_group,
                    "available": available,
                    "donation_history": []
                })
            else:  # receiver
                user_data.update({
                    "organization": organization,
                    "request_history": []
                })
            
            # Save user data to Firestore
            db = database.get_firestore_db()
            db.collection('users').document(user['localId']).set(user_data)
            
            st.success("Account created successfully! You can now log in.")
            
        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                st.error("This email is already registered. Please try logging in instead or use a different email address.")
            elif "INVALID_EMAIL" in error_message:
                st.error("Please enter a valid email address.")
            elif "WEAK_PASSWORD" in error_message:
                st.error("Password should be at least 6 characters long.")
            else:
                st.error(f"Registration failed: {error_message}")

def logout():
    for key in ['user', 'user_role', 'user_id', 'logged_in']:
        if key in st.session_state:
            del st.session_state[key]
    
    display_message("success", "Logged out successfully!")
