# Blood Bank Management System - Installation Guide

## Prerequisites

Before installing the Blood Bank Management System, ensure you have the following:

1. **Python 3.8+** installed on your computer
2. **Firebase Account** - for authentication and database services
3. **Internet connection** - to download dependencies and connect to Firebase

## Installation Steps

### 1. Download and Extract the Code

1. Download the `blood_bank_system.zip` file to your local computer
2. Extract the ZIP file to a folder of your choice
3. Open a terminal/command prompt and navigate to the extracted folder

### 2. Set Up Python Environment (Recommended)

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Required Dependencies

```bash
# Install all required packages
pip install streamlit firebase-admin pyrebase4 pandas plotly pycryptodome
```

### 4. Set Up Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/) and create a new project
2. Set up Authentication:
   - Go to Authentication > Sign-in method
   - Enable Email/Password authentication
3. Set up Firestore Database:
   - Go to Firestore Database > Create database
   - Start in production mode
   - Choose a location close to your users
4. Get your Firebase configuration:
   - Go to Project Settings > General
   - Scroll down to "Your apps" section
   - Click on the web app icon (</>) to create a web app
   - Register the app with a nickname
   - Copy the Firebase configuration object (it contains apiKey, authDomain, etc.)

### 5. Configure the Application

1. Open the `database.py` file in a text editor
2. Update the Firebase configuration with your credentials:

```python
# Look for this section and replace with your own Firebase config
firebase_config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_PROJECT_ID.appspot.com",
    "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
    "appId": "YOUR_APP_ID",
    "databaseURL": "https://YOUR_PROJECT_ID.firebaseio.com"
}
```

### 6. Ensure Streamlit Configuration

Make sure the `.streamlit` directory contains a `config.toml` file with:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

If for some reason this file is missing, create it in a `.streamlit` folder.

### 7. Run the Application

```bash
# Run the Streamlit application
streamlit run app.py
```

Your browser should automatically open to `http://localhost:5000` showing the Blood Bank Management System.

## Using the System

1. **First-time setup**:
   - Register as an admin to set up the system
   - Add initial blood inventory
   - Configure system settings

2. **Regular Operations**:
   - Register donors and receivers
   - Process blood donations
   - Manage blood requests
   - Generate reports

## Troubleshooting

If you encounter any issues:

1. **Firebase Connection Problems**:
   - Verify your internet connection
   - Check that your Firebase configuration is correct
   - Ensure Firebase services (Auth, Firestore) are enabled

2. **Package Installation Issues**:
   - Try installing packages one by one
   - For Windows users, you may need Microsoft C++ Build Tools for some packages

3. **Application Not Starting**:
   - Check Python version (3.8+ required)
   - Verify all dependencies are installed
   - Check for errors in the terminal

## Need Help?

Refer to the full documentation in the `DOCUMENTATION.md` file for detailed information about the system architecture, database schema, and application workflows.