from datetime import datetime
from models import get_all_donors, get_all_blood_requests

# Blood type compatibility matrix
BLOOD_COMPATIBILITY = {
    'A+': ['A+', 'AB+'],
    'A-': ['A+', 'A-', 'AB+', 'AB-'],
    'B+': ['B+', 'AB+'],
    'B-': ['B+', 'B-', 'AB+', 'AB-'],
    'AB+': ['AB+'],
    'AB-': ['AB+', 'AB-'],
    'O+': ['A+', 'B+', 'AB+', 'O+'],
    'O-': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
}

def find_compatible_donors(blood_type, location=None):
    """
    Find donors compatible with the requested blood type
    """
    all_donors = get_all_donors()
    compatible_donors = []
    
    for donor in all_donors:
        # Check if donor's blood type is compatible
        if blood_type in BLOOD_COMPATIBILITY.get(donor.blood_type, []):
            # Check if donor is approved, available, and can donate
            if donor.is_approved and donor.is_available and donor.can_donate():
                compatible_donors.append(donor)
    
    # Sort by priority: O- (universal donor) first, then by last donation date
    def donor_priority(donor):
        universal_bonus = 0 if donor.blood_type == 'O-' else 1
        last_donation_penalty = 0
        if donor.last_donation_date:
            days_since = (datetime.now() - donor.last_donation_date).days
            last_donation_penalty = -days_since  # More recent = higher penalty
        return (universal_bonus, last_donation_penalty)
    
    compatible_donors.sort(key=donor_priority)
    return compatible_donors

def get_dashboard_analytics():
    """
    Generate analytics data for dashboard
    """
    all_donors = get_all_donors()
    all_requests = get_all_blood_requests()
    
    # Basic counts
    total_donors = len(all_donors)
    approved_donors = len([d for d in all_donors if d.is_approved])
    pending_donors = len([d for d in all_donors if not d.is_approved])
    
    total_requests = len(all_requests)
    pending_requests = len([r for r in all_requests if r.status == 'pending'])
    fulfilled_requests = len([r for r in all_requests if r.status == 'fulfilled'])
    
    # Blood type distribution
    blood_type_distribution = {}
    for donor in all_donors:
        blood_type = donor.blood_type
        blood_type_distribution[blood_type] = blood_type_distribution.get(blood_type, 0) + 1
    
    # Urgency distribution
    urgency_distribution = {}
    for request in all_requests:
        urgency = request.urgency
        urgency_distribution[urgency] = urgency_distribution.get(urgency, 0) + 1
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now().replace(day=1)  # Simplified for demo
    recent_donors = len([d for d in all_donors if d.created_at >= thirty_days_ago])
    recent_requests = len([r for r in all_requests if r.created_at >= thirty_days_ago])
    
    return {
        'total_donors': total_donors,
        'approved_donors': approved_donors,
        'pending_donors': pending_donors,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'fulfilled_requests': fulfilled_requests,
        'blood_type_distribution': blood_type_distribution,
        'urgency_distribution': urgency_distribution,
        'recent_donors': recent_donors,
        'recent_requests': recent_requests
    }

def get_critical_alerts():
    """
    Get critical alerts for admin dashboard
    """
    from models import get_blood_inventory
    
    alerts = []
    inventory = get_blood_inventory()
    
    # Check for low inventory levels
    for blood_type, data in inventory.items():
        if data['units'] < 20:
            alerts.append({
                'type': 'low_inventory',
                'message': f'Low inventory for {blood_type}: Only {data["units"]} units available',
                'severity': 'critical' if data['units'] < 10 else 'warning'
            })
    
    # Check for urgent requests
    urgent_requests = [r for r in get_all_blood_requests() 
                      if r.urgency == 'critical' and r.status == 'pending']
    
    for request in urgent_requests:
        alerts.append({
            'type': 'urgent_request',
            'message': f'Critical blood request for {request.blood_type} - {request.patient_name}',
            'severity': 'critical'
        })
    
    return alerts

def validate_donor_data(data):
    """
    Validate donor registration data
    """
    errors = []
    
    required_fields = ['blood_type', 'weight', 'age', 'phone', 'address']
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field.replace("_", " ").title()} is required')
    
    if data.get('weight'):
        try:
            weight = float(data['weight'])
            if weight < 50:  # Minimum weight requirement
                errors.append('Weight must be at least 50 kg')
        except ValueError:
            errors.append('Weight must be a valid number')
    
    if data.get('age'):
        try:
            age = int(data['age'])
            if age < 18 or age > 65:
                errors.append('Age must be between 18 and 65 years')
        except ValueError:
            errors.append('Age must be a valid number')
    
    valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    if data.get('blood_type') not in valid_blood_types:
        errors.append('Please select a valid blood type')
    
    return errors

def validate_blood_request_data(data):
    """
    Validate blood request data
    """
    errors = []
    
    required_fields = ['patient_name', 'blood_type', 'units_needed', 'urgency', 'hospital', 'contact_phone']
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field.replace("_", " ").title()} is required')
    
    if data.get('units_needed'):
        try:
            units = int(data['units_needed'])
            if units < 1 or units > 10:
                errors.append('Units needed must be between 1 and 10')
        except ValueError:
            errors.append('Units needed must be a valid number')
    
    valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    if data.get('blood_type') not in valid_blood_types:
        errors.append('Please select a valid blood type')
    
    valid_urgency = ['normal', 'urgent', 'critical']
    if data.get('urgency') not in valid_urgency:
        errors.append('Please select a valid urgency level')
    
    return errors
