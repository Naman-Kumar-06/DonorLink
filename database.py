import os
import firebase_admin
from firebase_admin import credentials, firestore, auth as admin_auth
import pyrebase4
from datetime import datetime

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyBQTVqNM-vlWcHXLvYqM8kGkPCX_VVROcQ",
    "authDomain": "bloodbank9090.firebaseapp.com",
    "projectId": "bloodbank9090",
    "storageBucket": "bloodbank9090.firebasestorage.app",
    "messagingSenderId": "268077674400",
    "appId": "1:268077674400:web:54421a2a982b140b6b3ec5",
    "measurementId": "G-XY4QZ9Q785",
    "databaseURL": ""  # Required for Pyrebase initialization but not used
}

# Global variables for Firebase services
firebase_app = None
firestore_db = None
firebase_auth = None

def initialize_firebase():
    global firebase_app, firestore_db, firebase_auth
    
    # Only initialize the Firebase Auth for client operations
    # Skip admin SDK initialization to avoid metadata service dependency
    
    # Initialize Pyrebase for client-side authentication
    if not firebase_auth:
        try:
            firebase = pyrebase.initialize_app(firebase_config)
            firebase_auth = firebase.auth()
            print("Firebase Auth initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase Auth: {e}")
    
    return True

def get_firestore_db():
    # Since we're not using Firebase Admin SDK, we'll use a mock database for now
    # In a real application, you would configure proper Firebase credentials
    
    # Return a mock database object with minimal functionality for demo purposes
    class MockFirestore:
        def collection(self, collection_name):
            return MockCollection(collection_name)
    
    class MockCollection:
        def __init__(self, name):
            self.name = name
        
        def document(self, doc_id=""):
            return MockDocument(doc_id)
        
        def where(self, field, op, value):
            return self
        
        def get(self):
            return []
        
        def order_by(self, field, direction=None):
            return self
    
    class MockDocument:
        def __init__(self, doc_id):
            self.id = doc_id
            self.exists = False
        
        def get(self):
            return self
        
        def set(self, data, merge=False):
            return True
        
        def update(self, data):
            return True
        
        def to_dict(self):
            return {}
            
        def collection(self, collection_name):
            # Support for nested collections (like notifications)
            return MockCollection(collection_name)
    
    return MockFirestore()

def get_auth():
    if not firebase_auth:
        initialize_firebase()
    return firebase_auth

def get_admin_auth():
    return admin_auth

def get_server_timestamp():
    # Since we're not using Firebase Admin SDK, return current datetime
    from datetime import datetime
    return datetime.now()

# User Management Functions
def get_user_by_id(user_id):
    db = get_firestore_db()
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        return user_doc.to_dict()
    return None

def update_user_profile(user_id, data):
    db = get_firestore_db()
    db.collection('users').document(user_id).update(data)
    return True

# Blood Inventory Functions
def get_blood_inventory():
    db = get_firestore_db()
    inventory_ref = db.collection('inventory').document('blood_inventory').get()
    if inventory_ref.exists:
        return inventory_ref.to_dict()
    return {}

def update_blood_inventory(inventory_data):
    db = get_firestore_db()
    db.collection('inventory').document('blood_inventory').set(inventory_data, merge=True)
    return True

# Blood Request Functions
def create_blood_request(request_data):
    db = get_firestore_db()
    request_ref = db.collection('blood_requests').document()
    request_data['request_id'] = request_ref.id
    request_data['created_at'] = get_server_timestamp()
    request_data['status'] = 'pending'
    request_ref.set(request_data)
    
    # Update user's request history
    db.collection('users').document(request_data['user_id']).update({
        'request_history': [
            {
                'request_id': request_ref.id,
                'blood_group': request_data['blood_group'],
                'units': request_data['units'],
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
        ]
    })
    
    return request_ref.id

def get_blood_requests(status=None):
    db = get_firestore_db()
    if status:
        requests = db.collection('blood_requests').where('status', '==', status).get()
    else:
        requests = db.collection('blood_requests').get()
    
    return [doc.to_dict() for doc in requests]

def get_blood_request(request_id):
    db = get_firestore_db()
    request_doc = db.collection('blood_requests').document(request_id).get()
    if request_doc.exists:
        return request_doc.to_dict()
    return None

def update_blood_request(request_id, data):
    db = get_firestore_db()
    db.collection('blood_requests').document(request_id).update(data)
    
    # Update request in user's history if status is changing
    if 'status' in data:
        request_doc = db.collection('blood_requests').document(request_id).get()
        if request_doc.exists:
            request_data = request_doc.to_dict()
            user_id = request_data['user_id']
            user_doc = db.collection('users').document(user_id).get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                if 'request_history' in user_data:
                    for i, req in enumerate(user_data['request_history']):
                        if req.get('request_id') == request_id:
                            user_data['request_history'][i]['status'] = data['status']
                            db.collection('users').document(user_id).update({
                                'request_history': user_data['request_history']
                            })
                            break
    
    return True

# Donor Functions
def get_available_donors(blood_group=None):
    db = get_firestore_db()
    if blood_group:
        donors = db.collection('users').where('role', '==', 'donor').where('available', '==', True).where('blood_group', '==', blood_group).get()
    else:
        donors = db.collection('users').where('role', '==', 'donor').where('available', '==', True).get()
    
    return [doc.to_dict() for doc in donors]

def record_donation(donor_id, donation_data):
    db = get_firestore_db()
    donation_data['created_at'] = get_server_timestamp()
    
    # Add donation to donor's history
    db.collection('users').document(donor_id).update({
        'donation_history': [donation_data]
    })
    
    # Update blood inventory
    inventory_ref = db.collection('inventory').document('blood_inventory')
    inventory = inventory_ref.get()
    
    if inventory.exists:
        inventory_data = inventory.to_dict()
        blood_group = donation_data['blood_group']
        
        if blood_group in inventory_data:
            inventory_data[blood_group] = inventory_data[blood_group] + donation_data['units']
        else:
            inventory_data[blood_group] = donation_data['units']
        
        inventory_ref.set(inventory_data, merge=True)
    else:
        inventory_ref.set({
            donation_data['blood_group']: donation_data['units']
        })
    
    return True

# Notification Functions
def create_notification(user_id, notification_data):
    db = get_firestore_db()
    notification_data['created_at'] = get_server_timestamp()
    notification_data['read'] = False
    
    notification_ref = db.collection('users').document(user_id).collection('notifications').document()
    notification_data['id'] = notification_ref.id
    notification_ref.set(notification_data)
    
    return notification_ref.id

def get_notifications(user_id):
    db = get_firestore_db()
    notifications = db.collection('users').document(user_id).collection('notifications').order_by('created_at').get()
    
    return [doc.to_dict() for doc in notifications]

def mark_notification_as_read(user_id, notification_id):
    db = get_firestore_db()
    db.collection('users').document(user_id).collection('notifications').document(notification_id).update({
        'read': True
    })
    
    return True
