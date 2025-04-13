import streamlit as st
import database
import dashboard
from utils import display_message

def show_donor_dashboard():
    """Display the donor dashboard"""
    st.title("🩸 Donor Dashboard")
    
    # Show notifications
    if st.session_state.user_id:
        dashboard.show_notifications(st.session_state.user_id)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Profile", "Donation History", "Blood Requests"])
    
    # Profile Tab
    with tab1:
        show_donor_profile()
    
    # Donation History Tab
    with tab2:
        show_donation_history()
    
    # Blood Requests Tab
    with tab3:
        show_blood_requests()

def show_donor_profile():
    """Display and manage donor profile"""
    st.header("My Profile")
    
    user = st.session_state.user
    
    # Create form for updating profile
    with st.form(key="donor_profile_form"):
        name = st.text_input("Full Name", value=user.get('name', ''))
        email = st.text_input("Email", value=user.get('email', ''), disabled=True)
        phone = st.text_input("Phone Number", value=user.get('phone', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            blood_group = st.selectbox("Blood Group", 
                                       options=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                       index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(user.get('blood_group', 'A+')) if user.get('blood_group') else 0)
        
        with col2:
            available = st.checkbox("Available for donation", value=user.get('available', False))
        
        address = st.text_area("Address", value=user.get('address', ''))
        city = st.text_input("City", value=user.get('city', ''))
        
        submit_button = st.form_submit_button(label="Update Profile")
        
        if submit_button:
            # Update user profile in Firestore
            updated_data = {
                "name": name,
                "phone": phone,
                "blood_group": blood_group,
                "available": available,
                "address": address,
                "city": city
            }
            
            try:
                database.update_user_profile(st.session_state.user_id, updated_data)
                st.session_state.user.update(updated_data)
                display_message("success", "Profile updated successfully!")
            except Exception as e:
                display_message("error", f"Failed to update profile: {str(e)}")

def show_donation_history():
    """Display donation history for the donor"""
    st.header("Donation History")
    
    user = st.session_state.user
    donation_history = user.get('donation_history', [])
    
    if not donation_history:
        st.info("You haven't made any donations yet.")
    else:
        # Sort by date, newest first
        donation_history.sort(key=lambda x: x.get('donation_date', ''), reverse=True)
        
        for i, donation in enumerate(donation_history):
            with st.expander(f"Donation on {donation.get('donation_date', 'Unknown date')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Blood Group", donation.get('blood_group', 'Unknown'))
                
                with col2:
                    st.metric("Units Donated", donation.get('units', 0))
                
                with col3:
                    st.metric("Location", donation.get('location', 'Unknown'))
                
                if donation.get('notes'):
                    st.write("Notes:", donation.get('notes'))

def show_blood_requests():
    """Display blood requests that match the donor's blood group"""
    st.header("Blood Requests")
    
    user = st.session_state.user
    blood_group = user.get('blood_group')
    
    if not blood_group:
        st.warning("Please update your blood group in your profile to see matching requests.")
        return
    
    # Get all pending blood requests
    all_requests = database.get_blood_requests('pending')
    
    # Filter for compatible blood types
    compatible_requests = []
    
    # Blood type compatibility chart: donor -> can donate to
    compatibility = {
        "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
        "O+": ["O+", "A+", "B+", "AB+"],
        "A-": ["A-", "A+", "AB-", "AB+"],
        "A+": ["A+", "AB+"],
        "B-": ["B-", "B+", "AB-", "AB+"],
        "B+": ["B+", "AB+"],
        "AB-": ["AB-", "AB+"],
        "AB+": ["AB+"]
    }
    
    # Only show requests that the donor can help with
    compatible_blood_types = compatibility.get(blood_group, [])
    for request in all_requests:
        if request.get('blood_group') in compatible_blood_types:
            compatible_requests.append(request)
    
    if not compatible_requests:
        st.info("No compatible blood requests at the moment.")
        return
    
    # Display compatible requests
    st.subheader("Matching Blood Requests")
    st.write(f"Based on your blood type ({blood_group}), you can help with the following requests:")
    
    for request in compatible_requests:
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                st.metric("Blood Group", request.get('blood_group', 'Unknown'))
            
            with col2:
                st.metric("Units Needed", request.get('units', 0))
            
            with col3:
                st.metric("Urgency", request.get('urgency', 'Normal'))
            
            with col4:
                st.metric("Location", request.get('location', 'Unknown'))
            
            # Show action button if donor is available
            if user.get('available', False):
                if st.button("I want to donate", key=f"donate_{request.get('request_id')}"):
                    # Create notification for requester
                    notification_data = {
                        'message': f"Donor {user.get('name')} with blood group {blood_group} has offered to donate for your request.",
                        'type': 'donor_offer',
                        'request_id': request.get('request_id')
                    }
                    
                    try:
                        database.create_notification(request.get('user_id'), notification_data)
                        
                        # Also notify admin
                        admin_notification = {
                            'message': f"Donor {user.get('name')} has offered to donate for request ID {request.get('request_id')}",
                            'type': 'donor_offer',
                            'request_id': request.get('request_id')
                        }
                        
                        # Get admin users
                        db = database.get_firestore_db()
                        admins = db.collection('users').where('role', '==', 'admin').get()
                        
                        for admin in admins:
                            database.create_notification(admin.id, admin_notification)
                        
                        display_message("success", "Your donation offer has been sent to the requester!")
                    except Exception as e:
                        display_message("error", f"Failed to send donation offer: {str(e)}")
            else:
                st.warning("Update your profile to mark yourself as available for donation.")
            
            st.divider()
