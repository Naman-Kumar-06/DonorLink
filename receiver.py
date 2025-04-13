import streamlit as st
import database
import dashboard
from utils import display_message

def show_receiver_dashboard():
    """Display the receiver dashboard"""
    st.title("🏥 Receiver Dashboard")
    
    # Show notifications
    if st.session_state.user_id:
        dashboard.show_notifications(st.session_state.user_id)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "New Request", "My Requests", "Available Donors"])
    
    # Profile Tab
    with tab1:
        show_receiver_profile()
    
    # New Request Tab
    with tab2:
        show_request_form()
    
    # My Requests Tab
    with tab3:
        show_my_requests()
    
    # Available Donors Tab
    with tab4:
        show_available_donors()

def show_receiver_profile():
    """Display and manage receiver profile"""
    st.header("My Profile")
    
    user = st.session_state.user
    
    # Create form for updating profile
    with st.form(key="receiver_profile_form"):
        name = st.text_input("Contact Person Name", value=user.get('name', ''))
        email = st.text_input("Email", value=user.get('email', ''), disabled=True)
        organization = st.text_input("Organization/Hospital Name", value=user.get('organization', ''))
        phone = st.text_input("Phone Number", value=user.get('phone', ''))
        address = st.text_area("Address", value=user.get('address', ''))
        city = st.text_input("City", value=user.get('city', ''))
        
        submit_button = st.form_submit_button(label="Update Profile")
        
        if submit_button:
            # Update user profile in Firestore
            updated_data = {
                "name": name,
                "organization": organization,
                "phone": phone,
                "address": address,
                "city": city
            }
            
            try:
                database.update_user_profile(st.session_state.user_id, updated_data)
                st.session_state.user.update(updated_data)
                display_message("success", "Profile updated successfully!")
            except Exception as e:
                display_message("error", f"Failed to update profile: {str(e)}")

def show_request_form():
    """Display form to create a new blood request"""
    st.header("Create New Blood Request")
    
    user = st.session_state.user
    
    with st.form(key="blood_request_form"):
        blood_group = st.selectbox("Blood Group Needed", 
                                   options=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        
        units = st.number_input("Units Required", min_value=1, max_value=10, value=1)
        
        urgency = st.select_slider("Urgency Level", 
                                  options=["Low", "Normal", "High", "Critical"],
                                  value="Normal")
        
        # Default to user's address but allow changing
        location = st.text_input("Delivery Location", value=user.get('address', ''))
        
        purpose = st.text_area("Purpose of Request")
        
        patient_name = st.text_input("Patient Name (Optional)")
        
        submit_button = st.form_submit_button(label="Submit Request")
        
        if submit_button:
            if not location:
                st.error("Please provide a delivery location.")
                return
            
            # Create request data
            request_data = {
                "blood_group": blood_group,
                "units": units,
                "urgency": urgency,
                "location": location,
                "purpose": purpose,
                "patient_name": patient_name,
                "user_id": st.session_state.user_id,
                "requester_name": user.get('name'),
                "organization": user.get('organization'),
                "contact_phone": user.get('phone')
            }
            
            try:
                # Submit request to database
                request_id = database.create_blood_request(request_data)
                
                # Notify admin about new request
                admin_notification = {
                    'message': f"New blood request: {units} units of {blood_group} with {urgency} urgency.",
                    'type': 'new_request',
                    'request_id': request_id
                }
                
                # Get admin users
                db = database.get_firestore_db()
                admins = db.collection('users').where('role', '==', 'admin').get()
                
                for admin in admins:
                    database.create_notification(admin.id, admin_notification)
                
                # Also notify matching donors
                donors = database.get_available_donors()
                
                # Blood type compatibility chart: recipient <- can receive from
                compatibility = {
                    "O-": ["O-"],
                    "O+": ["O-", "O+"],
                    "A-": ["O-", "A-"],
                    "A+": ["O-", "O+", "A-", "A+"],
                    "B-": ["O-", "B-"],
                    "B+": ["O-", "O+", "B-", "B+"],
                    "AB-": ["O-", "A-", "B-", "AB-"],
                    "AB+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
                }
                
                compatible_donors = [
                    d for d in donors if d.get('blood_group') in compatibility.get(blood_group, [])
                ]
                
                for donor in compatible_donors:
                    donor_id = donor.get('id')
                    if donor_id:
                        donor_notification = {
                            'message': f"Urgent blood request: {units} units of {blood_group} with {urgency} urgency. Your blood type is compatible!",
                            'type': 'compatible_request',
                            'request_id': request_id
                        }
                        database.create_notification(donor_id, donor_notification)
                
                display_message("success", "Blood request submitted successfully!")
                
            except Exception as e:
                display_message("error", f"Failed to submit request: {str(e)}")

def show_my_requests():
    """Display the receiver's blood requests"""
    st.header("My Blood Requests")
    
    # Get all requests for this user
    requests_df = dashboard.display_blood_requests(user_id=st.session_state.user_id, role='receiver')
    
    if requests_df is None or requests_df.empty:
        return
    
    # Allow cancelling pending requests
    st.subheader("Cancel Request")
    
    # Filter only pending requests
    pending_requests = requests_df[requests_df['Status'] == 'pending']
    
    if pending_requests.empty:
        st.info("You have no pending requests that can be cancelled.")
        return
    
    # Create selection for cancellation
    request_options = {row['Request ID']: f"{row['Blood Group']} - {row['Units']} units - {row['Status']}" 
                       for _, row in pending_requests.iterrows()}
    
    selected_request = st.selectbox("Select request to cancel:", 
                                    options=list(request_options.keys()),
                                    format_func=lambda x: request_options[x])
    
    if st.button("Cancel Selected Request"):
        try:
            # Update request status
            database.update_blood_request(selected_request, {'status': 'cancelled'})
            
            display_message("success", "Request cancelled successfully!")
            st.rerun()
        except Exception as e:
            display_message("error", f"Failed to cancel request: {str(e)}")

def show_available_donors():
    """Display list of available donors"""
    st.header("Available Donors")
    
    # Get available donors
    donors = database.get_available_donors()
    
    if not donors:
        st.info("No donors are currently available.")
        return
    
    # Display donors grouped by blood type
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    
    for blood_group in blood_groups:
        # Filter donors by blood group
        group_donors = [d for d in donors if d.get('blood_group') == blood_group]
        
        if group_donors:
            with st.expander(f"{blood_group} Donors ({len(group_donors)})"):
                for donor in group_donors:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**{donor.get('name', 'Unknown')}**")
                        st.caption(f"Location: {donor.get('city', 'Unknown')}")
                    
                    with col2:
                        # Show donation history count
                        donation_history = donor.get('donation_history', [])
                        st.write(f"Previous donations: {len(donation_history)}")
                    
                    with col3:
                        # Contact button
                        if st.button("Request", key=f"request_{donor.get('id', '')}"):
                            try:
                                # Create notification for donor
                                notification_data = {
                                    'message': f"{st.session_state.user.get('name')} from {st.session_state.user.get('organization')} is requesting your help for a blood donation. Please check the Blood Requests tab.",
                                    'type': 'donation_request'
                                }
                                
                                database.create_notification(donor.get('id', ''), notification_data)
                                display_message("success", "Request sent to donor!")
                            except Exception as e:
                                display_message("error", f"Failed to send request: {str(e)}")
                    
                    st.divider()
