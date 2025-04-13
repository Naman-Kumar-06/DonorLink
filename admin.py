import streamlit as st
import pandas as pd
import plotly.express as px
import database
import dashboard
from utils import display_message

def show_admin_dashboard():
    """Display the admin dashboard"""
    st.title("⚕️ Admin Dashboard")
    
    # Show notifications
    if st.session_state.user_id:
        dashboard.show_notifications(st.session_state.user_id)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Inventory", "Blood Requests", "Donor Management", 
        "Receiver Management", "Reports"
    ])
    
    # Inventory Tab
    with tab1:
        show_inventory_management()
    
    # Blood Requests Tab
    with tab2:
        show_blood_request_management()
    
    # Donor Management Tab
    with tab3:
        show_donor_management()
    
    # Receiver Management Tab
    with tab4:
        show_receiver_management()
    
    # Reports Tab
    with tab5:
        show_reports()

def show_inventory_management():
    """Display and manage blood inventory"""
    st.header("Blood Inventory Management")
    
    # Show current inventory
    dashboard.show_blood_inventory()
    
    # Add form to update inventory
    st.subheader("Update Inventory")
    
    with st.form(key="update_inventory_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            blood_group = st.selectbox("Blood Group", 
                                      options=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        
        with col2:
            action = st.radio("Action", options=["Add", "Remove"])
        
        units = st.number_input("Units", min_value=1, max_value=100, value=1)
        
        notes = st.text_area("Notes")
        
        submit_button = st.form_submit_button(label="Update Inventory")
        
        if submit_button:
            try:
                # Get current inventory
                inventory = database.get_blood_inventory()
                
                # Update inventory based on action
                current_units = inventory.get(blood_group, 0)
                
                if action == "Add":
                    new_units = current_units + units
                else:  # Remove
                    if current_units < units:
                        st.error(f"Cannot remove {units} units. Only {current_units} units available.")
                        return
                    new_units = current_units - units
                
                # Update database
                inventory[blood_group] = new_units
                database.update_blood_inventory(inventory)
                
                display_message("success", f"Inventory updated! {blood_group}: {current_units} → {new_units} units")
                st.rerun()
                
            except Exception as e:
                display_message("error", f"Failed to update inventory: {str(e)}")

def show_blood_request_management():
    """Manage blood requests"""
    st.header("Blood Request Management")
    
    # Create filter for request status
    status_filter = st.selectbox(
        "Filter by Status",
        options=["All", "Pending", "Approved", "Completed", "Rejected", "Cancelled"],
        index=0
    )
    
    # Convert status to lowercase for database query
    db_status = status_filter.lower() if status_filter != "All" else None
    
    # Display blood requests
    requests_df = dashboard.display_blood_requests(status=db_status)
    
    if requests_df is None or requests_df.empty:
        return
    
    # Allow admin to update request status
    st.subheader("Update Request Status")
    
    # Select a request to update
    request_options = {row['Request ID']: f"{row['Blood Group']} - {row['Units']} units - {row['Status']} - {row['Requested By']}" 
                       for _, row in requests_df.iterrows()}
    
    selected_request_id = st.selectbox("Select Request:", 
                                     options=list(request_options.keys()),
                                     format_func=lambda x: request_options[x])
    
    # Get the full request data
    selected_request = None
    for _, row in requests_df.iterrows():
        if row['Request ID'] == selected_request_id:
            selected_request = row['Full Data']
            break
    
    if selected_request:
        # Show the request details
        st.write("### Request Details")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Blood Group", selected_request.get('blood_group', 'Unknown'))
            st.metric("Units", selected_request.get('units', 0))
        
        with col2:
            st.metric("Urgency", selected_request.get('urgency', 'Normal'))
            st.metric("Location", selected_request.get('location', 'Unknown'))
        
        with col3:
            st.metric("Status", selected_request.get('status', 'Unknown').capitalize())
            st.metric("Requested By", selected_request.get('requester_name', 'Unknown'))
        
        # Show additional details
        if selected_request.get('purpose'):
            st.write("**Purpose:**", selected_request.get('purpose'))
        
        if selected_request.get('patient_name'):
            st.write("**Patient Name:**", selected_request.get('patient_name'))
        
        # Update status form
        st.write("### Update Status")
        
        current_status = selected_request.get('status', '').lower()
        
        # Determine available status options based on current status
        if current_status == 'pending':
            status_options = ["Approved", "Rejected"]
        elif current_status == 'approved':
            status_options = ["Completed", "Cancelled"]
        else:
            status_options = []
        
        if status_options:
            new_status = st.radio("New Status", options=status_options)
            
            notes = st.text_area("Notes (will be sent to requester)")
            
            if st.button("Update Status"):
                try:
                    # Update request status
                    database.update_blood_request(selected_request_id, {
                        'status': new_status.lower(),
                        'admin_notes': notes
                    })
                    
                    # Create notification for requester
                    notification_data = {
                        'message': f"Your blood request ({selected_request.get('blood_group')}, {selected_request.get('units')} units) has been {new_status.lower()}. {notes}",
                        'type': 'request_update',
                        'request_id': selected_request_id
                    }
                    
                    database.create_notification(selected_request.get('user_id'), notification_data)
                    
                    # If approved, check inventory and update
                    if new_status.lower() == 'approved':
                        # Get current inventory
                        inventory = database.get_blood_inventory()
                        
                        # Check if enough blood is available
                        blood_group = selected_request.get('blood_group')
                        units_needed = selected_request.get('units', 0)
                        
                        if blood_group in inventory and inventory[blood_group] >= units_needed:
                            # Update inventory
                            inventory[blood_group] -= units_needed
                            database.update_blood_inventory(inventory)
                            
                            st.success(f"Request approved and inventory updated. {blood_group}: {units_needed} units deducted.")
                        else:
                            st.warning(f"Request approved but insufficient inventory. Please find donors or update inventory.")
                    
                    display_message("success", f"Request status updated to {new_status}!")
                    st.rerun()
                    
                except Exception as e:
                    display_message("error", f"Failed to update request: {str(e)}")
        else:
            st.info(f"This request is already {current_status} and cannot be updated further.")

def show_donor_management():
    """Manage donors"""
    st.header("Donor Management")
    
    # Get all donors
    db = database.get_firestore_db()
    donors = db.collection('users').where('role', '==', 'donor').get()
    
    if not donors:
        st.info("No donors registered in the system.")
        return
    
    # Convert to list for display
    donor_list = []
    for donor in donors:
        donor_data = donor.to_dict()
        donor_data['id'] = donor.id
        donor_list.append(donor_data)
    
    # Create search box
    search_term = st.text_input("Search donors by name, blood group, or city:")
    
    # Filter donors based on search
    if search_term:
        filtered_donors = []
        for donor in donor_list:
            if (search_term.lower() in donor.get('name', '').lower() or
                search_term.lower() in donor.get('blood_group', '').lower() or
                search_term.lower() in donor.get('city', '').lower()):
                filtered_donors.append(donor)
        donors_to_display = filtered_donors
    else:
        donors_to_display = donor_list
    
    # Display donors
    if not donors_to_display:
        st.info("No donors match your search criteria.")
        return
    
    # Show donor statistics
    st.subheader("Donor Statistics")
    
    total_donors = len(donor_list)
    available_donors = len([d for d in donor_list if d.get('available', False)])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Donors", total_donors)
    
    with col2:
        st.metric("Available Donors", available_donors)
    
    # Group donors by blood group
    blood_groups = {}
    for donor in donor_list:
        bg = donor.get('blood_group', 'Unknown')
        blood_groups[bg] = blood_groups.get(bg, 0) + 1
    
    # Display blood group distribution
    bg_data = pd.DataFrame({
        'Blood Group': list(blood_groups.keys()),
        'Count': list(blood_groups.values())
    })
    
    fig = px.pie(bg_data, names='Blood Group', values='Count', title='Donor Distribution by Blood Group')
    st.plotly_chart(fig, use_container_width=True)
    
    # Display donor list
    st.subheader(f"Donor List ({len(donors_to_display)})")
    
    for donor in donors_to_display:
        with st.expander(f"{donor.get('name', 'Unknown')} - {donor.get('blood_group', 'Unknown')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Contact Information**")
                st.write(f"Email: {donor.get('email', 'Unknown')}")
                st.write(f"Phone: {donor.get('phone', 'Unknown')}")
                st.write(f"Address: {donor.get('address', 'Unknown')}")
                st.write(f"City: {donor.get('city', 'Unknown')}")
            
            with col2:
                st.write("**Donation Status**")
                status = "Available" if donor.get('available', False) else "Not Available"
                st.write(f"Status: {status}")
                
                # Show donation history
                donation_history = donor.get('donation_history', [])
                st.write(f"Total Donations: {len(donation_history)}")
                
                if donation_history:
                    st.write("Last Donation:", donation_history[-1].get('donation_date', 'Unknown'))
            
            # Button to send notification
            notification_msg = st.text_area("Notification Message:", key=f"notify_{donor.get('id', '')}")
            
            if st.button("Send Notification", key=f"send_{donor.get('id', '')}"):
                if notification_msg:
                    try:
                        notification_data = {
                            'message': notification_msg,
                            'type': 'admin_message'
                        }
                        
                        database.create_notification(donor.get('id', ''), notification_data)
                        display_message("success", "Notification sent successfully!")
                    except Exception as e:
                        display_message("error", f"Failed to send notification: {str(e)}")
                else:
                    st.warning("Please enter a message to send.")

def show_receiver_management():
    """Manage receivers"""
    st.header("Receiver Management")
    
    # Get all receivers
    db = database.get_firestore_db()
    receivers = db.collection('users').where('role', '==', 'receiver').get()
    
    if not receivers:
        st.info("No receivers registered in the system.")
        return
    
    # Convert to list for display
    receiver_list = []
    for receiver in receivers:
        receiver_data = receiver.to_dict()
        receiver_data['id'] = receiver.id
        receiver_list.append(receiver_data)
    
    # Create search box
    search_term = st.text_input("Search receivers by name, organization, or city:")
    
    # Filter receivers based on search
    if search_term:
        filtered_receivers = []
        for receiver in receiver_list:
            if (search_term.lower() in receiver.get('name', '').lower() or
                search_term.lower() in receiver.get('organization', '').lower() or
                search_term.lower() in receiver.get('city', '').lower()):
                filtered_receivers.append(receiver)
        receivers_to_display = filtered_receivers
    else:
        receivers_to_display = receiver_list
    
    # Display receivers
    if not receivers_to_display:
        st.info("No receivers match your search criteria.")
        return
    
    # Show receiver statistics
    st.subheader("Receiver Statistics")
    
    total_receivers = len(receiver_list)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Receivers", total_receivers)
    
    with col2:
        # Count total requests
        total_requests = sum(len(r.get('request_history', [])) for r in receiver_list)
        st.metric("Total Requests", total_requests)
    
    # Display receiver list
    st.subheader(f"Receiver List ({len(receivers_to_display)})")
    
    for receiver in receivers_to_display:
        with st.expander(f"{receiver.get('name', 'Unknown')} - {receiver.get('organization', 'Unknown')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Contact Information**")
                st.write(f"Email: {receiver.get('email', 'Unknown')}")
                st.write(f"Phone: {receiver.get('phone', 'Unknown')}")
                st.write(f"Address: {receiver.get('address', 'Unknown')}")
                st.write(f"City: {receiver.get('city', 'Unknown')}")
            
            with col2:
                st.write("**Request History**")
                request_history = receiver.get('request_history', [])
                st.write(f"Total Requests: {len(request_history)}")
                
                if request_history:
                    # Count requests by status
                    status_counts = {}
                    for req in request_history:
                        status = req.get('status', 'unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    for status, count in status_counts.items():
                        st.write(f"{status.capitalize()}: {count}")
            
            # Button to send notification
            notification_msg = st.text_area("Notification Message:", key=f"notify_{receiver.get('id', '')}")
            
            if st.button("Send Notification", key=f"send_{receiver.get('id', '')}"):
                if notification_msg:
                    try:
                        notification_data = {
                            'message': notification_msg,
                            'type': 'admin_message'
                        }
                        
                        database.create_notification(receiver.get('id', ''), notification_data)
                        display_message("success", "Notification sent successfully!")
                    except Exception as e:
                        display_message("error", f"Failed to send notification: {str(e)}")
                else:
                    st.warning("Please enter a message to send.")

def show_reports():
    """Display reports and analytics"""
    st.header("Reports & Analytics")
    
    # Get necessary data
    db = database.get_firestore_db()
    
    # Get all blood requests
    all_requests = db.collection('blood_requests').get()
    requests_data = [req.to_dict() for req in all_requests]
    
    # Get all users
    all_donors = db.collection('users').where('role', '==', 'donor').get()
    donors_data = [donor.to_dict() for donor in all_donors]
    
    all_receivers = db.collection('users').where('role', '==', 'receiver').get()
    receivers_data = [receiver.to_dict() for receiver in all_receivers]
    
    # Get inventory
    inventory = database.get_blood_inventory()
    
    if not requests_data and not donors_data and not receivers_data and not inventory:
        st.info("Not enough data to generate reports.")
        return
    
    # Create tabs for different reports
    report_tab1, report_tab2, report_tab3, report_tab4 = st.tabs([
        "Blood Requests", "Donor Activity", "Inventory Trends", "User Growth"
    ])
    
    # Blood Requests Tab
    with report_tab1:
        if not requests_data:
            st.info("No blood requests data available.")
        else:
            st.subheader("Blood Request Statistics")
            
            # Process request data
            status_counts = {}
            blood_group_counts = {}
            urgency_counts = {}
            
            for req in requests_data:
                # Count by status
                status = req.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count by blood group
                blood_group = req.get('blood_group', 'unknown')
                blood_group_counts[blood_group] = blood_group_counts.get(blood_group, 0) + 1
                
                # Count by urgency
                urgency = req.get('urgency', 'normal')
                urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
            
            # Display status distribution
            status_df = pd.DataFrame({
                'Status': list(status_counts.keys()),
                'Count': list(status_counts.values())
            })
            
            fig1 = px.bar(
                status_df, 
                x='Status', 
                y='Count',
                title='Blood Requests by Status',
                color='Status'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Display blood group distribution
            col1, col2 = st.columns(2)
            
            with col1:
                blood_group_df = pd.DataFrame({
                    'Blood Group': list(blood_group_counts.keys()),
                    'Count': list(blood_group_counts.values())
                })
                
                fig2 = px.pie(
                    blood_group_df,
                    names='Blood Group',
                    values='Count',
                    title='Requests by Blood Group'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                urgency_df = pd.DataFrame({
                    'Urgency': list(urgency_counts.keys()),
                    'Count': list(urgency_counts.values())
                })
                
                fig3 = px.pie(
                    urgency_df,
                    names='Urgency',
                    values='Count',
                    title='Requests by Urgency Level'
                )
                st.plotly_chart(fig3, use_container_width=True)
    
    # Donor Activity Tab
    with report_tab2:
        if not donors_data:
            st.info("No donor data available.")
        else:
            st.subheader("Donor Activity")
            
            # Calculate donor statistics
            total_donors = len(donors_data)
            available_donors = len([d for d in donors_data if d.get('available', False)])
            
            total_donations = 0
            donation_by_blood_group = {}
            
            for donor in donors_data:
                donation_history = donor.get('donation_history', [])
                total_donations += len(donation_history)
                
                blood_group = donor.get('blood_group', 'Unknown')
                donation_by_blood_group[blood_group] = donation_by_blood_group.get(blood_group, 0) + len(donation_history)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Donors", total_donors)
            
            with col2:
                st.metric("Available Donors", available_donors)
                st.metric("Availability Rate", f"{int((available_donors / total_donors) * 100)}%" if total_donors > 0 else "0%")
            
            with col3:
                st.metric("Total Donations", total_donations)
                st.metric("Avg. Donations per Donor", f"{total_donations / total_donors:.1f}" if total_donors > 0 else "0")
            
            # Display donation distribution by blood group
            if donation_by_blood_group:
                donation_bg_df = pd.DataFrame({
                    'Blood Group': list(donation_by_blood_group.keys()),
                    'Donations': list(donation_by_blood_group.values())
                })
                
                fig4 = px.bar(
                    donation_bg_df,
                    x='Blood Group',
                    y='Donations',
                    title='Donations by Blood Group',
                    color='Blood Group'
                )
                st.plotly_chart(fig4, use_container_width=True)
    
    # Inventory Trends Tab
    with report_tab3:
        if not inventory:
            st.info("No inventory data available.")
        else:
            st.subheader("Current Blood Inventory")
            
            # Display inventory as bar chart
            inventory_df = pd.DataFrame({
                'Blood Group': list(inventory.keys()),
                'Units Available': list(inventory.values())
            })
            
            fig5 = px.bar(
                inventory_df,
                x='Blood Group',
                y='Units Available',
                title='Current Blood Inventory',
                color='Blood Group'
            )
            st.plotly_chart(fig5, use_container_width=True)
            
            # Calculate inventory metrics
            total_units = sum(inventory.values())
            
            # Determine which blood types are low
            low_inventory = []
            for bg, units in inventory.items():
                if units <= 3:  # Consider 3 or fewer units as low
                    low_inventory.append(bg)
            
            # Display metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Blood Units", total_units)
            
            with col2:
                st.metric("Blood Types with Low Stock", len(low_inventory))
                if low_inventory:
                    st.warning(f"Low stock alert for: {', '.join(low_inventory)}")
    
    # User Growth Tab
    with report_tab4:
        st.subheader("User Statistics")
        
        # Calculate user metrics
        total_users = len(donors_data) + len(receivers_data)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", total_users)
        
        with col2:
            st.metric("Donors", len(donors_data))
        
        with col3:
            st.metric("Receivers", len(receivers_data))
        
        # Display user distribution
        user_dist_df = pd.DataFrame({
            'User Type': ['Donors', 'Receivers'],
            'Count': [len(donors_data), len(receivers_data)]
        })
        
        fig6 = px.pie(
            user_dist_df,
            names='User Type',
            values='Count',
            title='User Distribution'
        )
        st.plotly_chart(fig6, use_container_width=True)
