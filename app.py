import streamlit as st
import auth
import dashboard
import database
import donor
import receiver
import admin
import utils
import download_code

# Set page config
st.set_page_config(
    page_title="Blood Bank Management System",
    page_icon="🩸",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize Firebase
database.initialize_firebase()

# Main function to render the appropriate page
def main():
    # Check for download code parameter
    params = st.query_params
    if "download_code" in params and params["download_code"] == "true":
        # Show download page
        download_code.download_code()
        return
    
    # Sidebar for navigation when logged in
    if st.session_state.logged_in:
        with st.sidebar:
            st.title(f"Welcome, {st.session_state.user.get('name', 'User')}")
            st.write(f"Role: {st.session_state.user_role.capitalize()}")
            
            if st.button("Logout"):
                auth.logout()
                st.rerun()
            
            # Add a divider
            st.markdown("---")
            
            # Add a link to download the code
            st.markdown("[📥 Download System Code](/?download_code=true)")
            st.markdown("<small>Get a copy of the entire codebase</small>", unsafe_allow_html=True)
    
    # Display appropriate page based on login status and user role
    if not st.session_state.logged_in:
        auth.show_auth_page()
    else:
        if st.session_state.user_role == "donor":
            donor.show_donor_dashboard()
        elif st.session_state.user_role == "receiver":
            receiver.show_receiver_dashboard()
        elif st.session_state.user_role == "admin":
            admin.show_admin_dashboard()
        else:
            st.error("Invalid user role. Please contact administrator.")
            auth.logout()
            st.rerun()

if __name__ == "__main__":
    main()
