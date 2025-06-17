import logging
from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app
from models import (
    create_user, get_user_by_email, get_user_by_id, create_donor, get_donor_by_user_id,
    create_blood_request, get_requests_by_user_id, get_all_donors, get_all_blood_requests,
    get_blood_request_by_id, get_blood_inventory, update_blood_inventory, donors, blood_requests
)
from utils import (
    find_compatible_donors, get_dashboard_analytics, get_critical_alerts,
    validate_donor_data, validate_blood_request_data
)
from email_service import (
    send_donor_approval_email, send_blood_request_notification, send_request_status_update
)

@app.before_request
def make_session_permanent():
    session.permanent = True

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        user = get_user_by_id(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        # Validation
        if not all([email, password, confirm_password, first_name, last_name]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if get_user_by_email(email):
            flash('Email address already registered.', 'error')
            return render_template('register.html')
        
        # Create user
        user = create_user(email, password, first_name, last_name)
        if user:
            session['user_id'] = user.id
            flash('Registration successful! Welcome to DonorLink.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html')
        
        user = get_user_by_email(email)
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_user_by_id(session['user_id'])
    
    if user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get user's donor profile
    donor = get_donor_by_user_id(user.id)
    
    # Get user's blood requests
    user_requests = get_requests_by_user_id(user.id)
    
    return render_template('dashboard.html', user=user, donor=donor, requests=user_requests)

@app.route('/profile')
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    donor = get_donor_by_user_id(user.id)
    return render_template('profile.html', user=user, donor=donor)

@app.route('/donor_registration', methods=['GET', 'POST'])
@login_required
def donor_registration():
    user = get_user_by_id(session['user_id'])
    existing_donor = get_donor_by_user_id(user.id)
    
    if existing_donor:
        flash('You are already registered as a donor.', 'info')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = {
            'blood_type': request.form.get('blood_type'),
            'weight': request.form.get('weight'),
            'age': request.form.get('age'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'medical_conditions': request.form.get('medical_conditions', ''),
            'medications': request.form.get('medications', ''),
            'last_donation_date': request.form.get('last_donation_date')
        }
        
        # Validate data
        errors = validate_donor_data(data)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('donor_registration.html')
        
        # Parse last donation date
        last_donation_date = None
        if data['last_donation_date']:
            try:
                last_donation_date = datetime.strptime(data['last_donation_date'], '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format for last donation.', 'error')
                return render_template('donor_registration.html')
        
        # Create donor
        donor = create_donor(
            user.id,
            data['blood_type'],
            data['weight'],
            data['age'],
            data['phone'],
            data['address'],
            last_donation_date
        )
        
        if donor:
            flash('Donor registration submitted successfully! Awaiting admin approval.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('donor_registration.html')

@app.route('/blood_request', methods=['GET', 'POST'])
@login_required
def blood_request():
    user = get_user_by_id(session['user_id'])
    
    if request.method == 'POST':
        data = {
            'patient_name': request.form.get('patient_name', '').strip(),
            'blood_type': request.form.get('blood_type'),
            'units_needed': request.form.get('units_needed'),
            'urgency': request.form.get('urgency'),
            'hospital': request.form.get('hospital', '').strip(),
            'contact_phone': request.form.get('contact_phone', '').strip(),
            'medical_condition': request.form.get('medical_condition', '').strip()
        }
        
        # Validate data
        errors = validate_blood_request_data(data)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('blood_request.html')
        
        # Create blood request
        blood_req = create_blood_request(
            user.id,
            data['patient_name'],
            data['blood_type'],
            data['units_needed'],
            data['urgency'],
            data['hospital'],
            data['contact_phone'],
            data['medical_condition']
        )
        
        if blood_req:
            flash('Blood request submitted successfully!', 'success')
            
            # Auto-approve and find compatible donors for urgent/critical requests
            if data['urgency'] in ['urgent', 'critical']:
                blood_req.status = 'approved'
                compatible_donors = find_compatible_donors(data['blood_type'])
                
                # Notify compatible donors
                for donor in compatible_donors[:10]:  # Limit to first 10 donors
                    donor_user = get_user_by_id(donor.user_id)
                    if donor_user:
                        send_blood_request_notification(
                            donor_user.email,
                            f"{donor_user.first_name} {donor_user.last_name}",
                            blood_req.to_dict()
                        )
                
                flash(f'Found {len(compatible_donors)} compatible donors. Notifications sent!', 'info')
            
            return redirect(url_for('dashboard'))
        else:
            flash('Request submission failed. Please try again.', 'error')
    
    return render_template('blood_request.html')

# Admin Routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    analytics = get_dashboard_analytics()
    alerts = get_critical_alerts()
    return render_template('admin_dashboard.html', analytics=analytics, alerts=alerts)

@app.route('/admin/donors')
@admin_required
def admin_donors():
    all_donors = get_all_donors()
    # Get user info for each donor
    donors_with_users = []
    for donor in all_donors:
        user = get_user_by_id(donor.user_id)
        if user:
            donors_with_users.append({
                'donor': donor,
                'user': user
            })
    
    return render_template('admin_donors.html', donors=donors_with_users)

@app.route('/admin/donors/approve/<int:donor_id>')
@admin_required
def approve_donor(donor_id):
    if donor_id in donors:
        donor = donors[donor_id]
        donor.is_approved = True
        
        # Send approval email
        user = get_user_by_id(donor.user_id)
        if user:
            send_donor_approval_email(
                user.email,
                f"{user.first_name} {user.last_name}",
                True
            )
        
        flash('Donor approved successfully!', 'success')
    else:
        flash('Donor not found.', 'error')
    
    return redirect(url_for('admin_donors'))

@app.route('/admin/donors/reject/<int:donor_id>')
@admin_required
def reject_donor(donor_id):
    if donor_id in donors:
        donor = donors[donor_id]
        donor.is_approved = False
        
        # Send rejection email
        user = get_user_by_id(donor.user_id)
        if user:
            send_donor_approval_email(
                user.email,
                f"{user.first_name} {user.last_name}",
                False
            )
        
        flash('Donor rejected.', 'info')
    else:
        flash('Donor not found.', 'error')
    
    return redirect(url_for('admin_donors'))

@app.route('/admin/requests')
@admin_required
def admin_requests():
    all_requests = get_all_blood_requests()
    # Get user info for each request
    requests_with_users = []
    for req in all_requests:
        user = get_user_by_id(req.user_id)
        if user:
            requests_with_users.append({
                'request': req,
                'user': user
            })
    
    return render_template('admin_requests.html', requests=requests_with_users)

@app.route('/admin/requests/approve/<int:request_id>')
@admin_required
def approve_request(request_id):
    if request_id in blood_requests:
        req = blood_requests[request_id]
        req.status = 'approved'
        
        # Find and notify compatible donors
        compatible_donors = find_compatible_donors(req.blood_type)
        
        for donor in compatible_donors[:10]:  # Limit to first 10 donors
            donor_user = get_user_by_id(donor.user_id)
            if donor_user:
                send_blood_request_notification(
                    donor_user.email,
                    f"{donor_user.first_name} {donor_user.last_name}",
                    req.to_dict()
                )
        
        # Notify requester
        requester = get_user_by_id(req.user_id)
        if requester:
            send_request_status_update(
                requester.email,
                f"{requester.first_name} {requester.last_name}",
                req.to_dict(),
                'approved'
            )
        
        flash(f'Request approved! Notified {len(compatible_donors)} compatible donors.', 'success')
    else:
        flash('Request not found.', 'error')
    
    return redirect(url_for('admin_requests'))

@app.route('/admin/requests/fulfill/<int:request_id>')
@admin_required
def fulfill_request(request_id):
    if request_id in blood_requests:
        req = blood_requests[request_id]
        req.status = 'fulfilled'
        req.fulfilled_at = datetime.now()
        
        # Notify requester
        requester = get_user_by_id(req.user_id)
        if requester:
            send_request_status_update(
                requester.email,
                f"{requester.first_name} {requester.last_name}",
                req.to_dict(),
                'fulfilled'
            )
        
        flash('Request marked as fulfilled!', 'success')
    else:
        flash('Request not found.', 'error')
    
    return redirect(url_for('admin_requests'))

@app.route('/admin/inventory')
@admin_required
def admin_inventory():
    inventory = get_blood_inventory()
    return render_template('admin_inventory.html', inventory=inventory)

@app.route('/admin/inventory/update', methods=['POST'])
@admin_required
def update_inventory():
    blood_type = request.form.get('blood_type')
    units = request.form.get('units')
    expiry_date = request.form.get('expiry_date')
    
    if not all([blood_type, units, expiry_date]):
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_inventory'))
    
    try:
        units = int(units)
        if units < 0:
            flash('Units must be a positive number.', 'error')
            return redirect(url_for('admin_inventory'))
    except ValueError:
        flash('Units must be a valid number.', 'error')
        return redirect(url_for('admin_inventory'))
    
    if update_blood_inventory(blood_type, units, expiry_date):
        flash(f'Inventory updated for {blood_type}.', 'success')
    else:
        flash('Failed to update inventory.', 'error')
    
    return redirect(url_for('admin_inventory'))

# API endpoints for analytics
@app.route('/api/analytics')
@admin_required
def api_analytics():
    analytics = get_dashboard_analytics()
    return jsonify(analytics)

@app.route('/api/blood_inventory')
@admin_required
def api_blood_inventory():
    inventory = get_blood_inventory()
    return jsonify(inventory)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
