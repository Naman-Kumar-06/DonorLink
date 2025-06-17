#!/usr/bin/env python3
"""
Simplified version to test basic functionality
"""
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Simple in-memory storage
users = {}
user_counter = 1

class SimpleUser:
    def __init__(self, email, password, first_name, last_name, is_admin=False):
        global user_counter
        self.id = user_counter
        user_counter += 1
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def get_user_by_email(email):
    for user in users.values():
        if user.email == email:
            return user
    return None

def create_user(email, password, first_name, last_name, is_admin=False):
    user = SimpleUser(email, password, first_name, last_name, is_admin)
    users[user.id] = user
    return user

# Initialize admin user
admin_user = create_user('admin@donorlink.com', 'admin123', 'System', 'Administrator', True)

@app.route('/')
def index():
    if 'user_id' in session:
        user = users.get(session['user_id'])
        return f"Welcome {user.first_name}! You are logged in."
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = get_user_by_email(email)
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    print("Starting simple Flask app...")
    app.run(host="0.0.0.0", port=5000, debug=True)