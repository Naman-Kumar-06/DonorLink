import streamlit as st
import os
import zipfile
import base64
from io import BytesIO

def download_code():
    """
    Creates a download button for users to download the entire codebase as a ZIP file.
    This function can be imported and called from the main application.
    """
    st.header("Download Code")
    st.write("Click the button below to download the entire Blood Bank Management System codebase.")
    
    # Create a BytesIO object to store the ZIP file
    buffer = BytesIO()
    
    # Create a new ZIP file
    with zipfile.ZipFile(buffer, 'w') as zipf:
        # Get all Python files in the current directory
        files_to_zip = []
        
        for file in os.listdir('.'):
            # Include Python files and documentation
            if file.endswith('.py') or file == 'DOCUMENTATION.md' or file == 'APPLICATION_FLOW.txt' or file == '.streamlit/config.toml':
                files_to_zip.append(file)
        
        # Add the .streamlit config
        if os.path.exists('.streamlit/config.toml'):
            zipf.write('.streamlit/config.toml', '.streamlit/config.toml')
        
        # Add all selected files to the ZIP
        for file in files_to_zip:
            if os.path.isfile(file):
                zipf.write(file)
    
    # Reset the buffer position to the beginning
    buffer.seek(0)
    
    # Create the download button
    st.download_button(
        label="Download Blood Bank System Code",
        data=buffer,
        file_name="blood_bank_system.zip",
        mime="application/zip"
    )
    
    # Add instructions for using the downloaded code
    st.markdown("""
    ### Instructions for using the downloaded code:
    
    1. **Extract the ZIP file** to a directory on your computer
    2. **Install the required packages**:
       ```
       pip install streamlit firebase-admin pyrebase pandas plotly
       ```
    3. **Set up Firebase**:
       - Create a Firebase project at [firebase.google.com](https://firebase.google.com)
       - Enable Authentication and Firestore Database
       - Update the Firebase configuration in `database.py`
    4. **Run the application**:
       ```
       streamlit run app.py
       ```
    
    For more detailed information, refer to the included DOCUMENTATION.md file.
    """)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Blood Bank System - Download Code",
        page_icon="🩸"
    )
    download_code()