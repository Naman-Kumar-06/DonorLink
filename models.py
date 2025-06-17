import threading
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# Thread-safe in-memory storage
_lock = threading.Lock()

# In-memory data storage
users = {}
donors = {}
blood_requests = {}
blood_inventory = {
    'A+': {'units': 50, 'expiry_date': '2024-07-15'},
    'A-': {'units': 30, 'expiry_date': '2024-07-10'},
    'B+': {'units': 40, 'expiry_date': '2024-07-20'},
    'B-': {'units': 25, 'expiry_date': '2024-07-18'},
    'AB+': {'units': 20, 'expiry_date': '2024-07-12'},
    'AB-': {'units': 15, 'expiry_date': '2024-07-25'},
    'O+': {'units': 60, 'expiry_date': '2024-07-22'},
    'O-': {'units': 35, 'expiry_date': '2024-07-14'}
}

# Counters for auto-incrementing IDs
_user_id_counter = 1
_donor_id_counter = 1
_request_id_counter = 1

class User:
    def __init__(self, email, password, first_name, last_name, is_admin=False):
        global _user_id_counter
        self.id = _user_id_counter
        _user_id_counter += 1
        
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
        self.created_at = datetime.now()
        self.is_active = True
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Donor:
    def __init__(self, user_id, blood_type, weight, age, phone, address, last_donation_date=None):
        global _donor_id_counter
        self.id = _donor_id_counter
        _donor_id_counter += 1
        
        self.user_id = user_id
        self.blood_type = blood_type
        self.weight = float(weight)
        self.age = int(age)
        self.phone = phone
        self.address = address
        self.last_donation_date = last_donation_date
        self.is_approved = False
        self.is_available = True
        self.created_at = datetime.now()
        
    def can_donate(self):
        """Check if donor is eligible to donate based on last donation date"""
        if not self.last_donation_date:
            return True
        
        # Must wait 56 days between donations
        days_since_last = (datetime.now() - self.last_donation_date).days
        return days_since_last >= 56
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'blood_type': self.blood_type,
            'weight': self.weight,
            'age': self.age,
            'phone': self.phone,
            'address': self.address,
            'last_donation_date': self.last_donation_date.isoformat() if self.last_donation_date else None,
            'is_approved': self.is_approved,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat(),
            'can_donate': self.can_donate()
        }

class BloodRequest:
    def __init__(self, user_id, patient_name, blood_type, units_needed, urgency, hospital, contact_phone, medical_condition):
        global _request_id_counter
        self.id = _request_id_counter
        _request_id_counter += 1
        
        self.user_id = user_id
        self.patient_name = patient_name
        self.blood_type = blood_type
        self.units_needed = int(units_needed)
        self.urgency = urgency  # 'critical', 'urgent', 'normal'
        self.hospital = hospital
        self.contact_phone = contact_phone
        self.medical_condition = medical_condition
        self.status = 'pending'  # 'pending', 'approved', 'fulfilled', 'cancelled'
        self.matched_donors = []
        self.created_at = datetime.now()
        self.fulfilled_at = None
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'patient_name': self.patient_name,
            'blood_type': self.blood_type,
            'units_needed': self.units_needed,
            'urgency': self.urgency,
            'hospital': self.hospital,
            'contact_phone': self.contact_phone,
            'medical_condition': self.medical_condition,
            'status': self.status,
            'matched_donors': self.matched_donors,
            'created_at': self.created_at.isoformat(),
            'fulfilled_at': self.fulfilled_at.isoformat() if self.fulfilled_at else None
        }

# Helper functions for data operations
def create_user(email, password, first_name, last_name, is_admin=False):
    with _lock:
        if email in [user.email for user in users.values()]:
            return None
        
        user = User(email, password, first_name, last_name, is_admin)
        users[user.id] = user
        return user

def get_user_by_email(email):
    with _lock:
        for user in users.values():
            if user.email == email:
                return user
        return None

def get_user_by_id(user_id):
    with _lock:
        return users.get(user_id)

def create_donor(user_id, blood_type, weight, age, phone, address, last_donation_date=None):
    with _lock:
        donor = Donor(user_id, blood_type, weight, age, phone, address, last_donation_date)
        donors[donor.id] = donor
        return donor

def get_donor_by_user_id(user_id):
    with _lock:
        for donor in donors.values():
            if donor.user_id == user_id:
                return donor
        return None

def get_all_donors():
    with _lock:
        return list(donors.values())

def create_blood_request(user_id, patient_name, blood_type, units_needed, urgency, hospital, contact_phone, medical_condition):
    with _lock:
        request = BloodRequest(user_id, patient_name, blood_type, units_needed, urgency, hospital, contact_phone, medical_condition)
        blood_requests[request.id] = request
        return request

def get_blood_request_by_id(request_id):
    with _lock:
        return blood_requests.get(request_id)

def get_requests_by_user_id(user_id):
    with _lock:
        return [req for req in blood_requests.values() if req.user_id == user_id]

def get_all_blood_requests():
    with _lock:
        return list(blood_requests.values())

def update_blood_inventory(blood_type, units, expiry_date):
    with _lock:
        if blood_type in blood_inventory:
            blood_inventory[blood_type]['units'] = units
            blood_inventory[blood_type]['expiry_date'] = expiry_date
            return True
        return False

def get_blood_inventory():
    with _lock:
        return blood_inventory.copy()

# Create default admin user on module load
try:
    admin_user = create_user(
        email='admin@donorlink.com',
        password='admin123',
        first_name='System',
        last_name='Administrator',
        is_admin=True
    )
    logging.info("Default admin user created successfully")
except Exception as e:
    logging.error(f"Error creating default admin user: {e}")
