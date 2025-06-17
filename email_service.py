import os
import logging
from flask_mail import Message
from app import mail, app

def send_email(subject, recipient, body, html_body=None):
    """
    Send email notification
    """
    try:
        with app.app_context():
            msg = Message(
                subject=subject,
                recipients=[recipient],
                body=body,
                html=html_body
            )
            mail.send(msg)
            logging.info(f"Email sent successfully to {recipient}")
            return True
    except Exception as e:
        logging.error(f"Failed to send email to {recipient}: {str(e)}")
        return False

def send_donor_approval_email(donor_email, donor_name, is_approved):
    """
    Send donor approval/rejection notification
    """
    if is_approved:
        subject = "Welcome to DonorLink - Your Application is Approved!"
        body = f"""
Dear {donor_name},

Congratulations! Your donor application has been approved.

You are now part of the DonorLink community and can start saving lives through blood donation.

Next steps:
1. Keep your profile updated
2. Check your dashboard for blood requests in your area
3. Maintain good health for regular donations

Thank you for joining our mission to save lives!

Best regards,
DonorLink Team
        """
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #dc3545;">Welcome to DonorLink!</h2>
            <p>Dear {donor_name},</p>
            <p><strong>Congratulations! Your donor application has been approved.</strong></p>
            <p>You are now part of the DonorLink community and can start saving lives through blood donation.</p>
            <h3>Next steps:</h3>
            <ul>
                <li>Keep your profile updated</li>
                <li>Check your dashboard for blood requests in your area</li>
                <li>Maintain good health for regular donations</li>
            </ul>
            <p>Thank you for joining our mission to save lives!</p>
            <p style="color: #dc3545;"><strong>DonorLink Team</strong></p>
        </div>
        """
    else:
        subject = "DonorLink Application Update"
        body = f"""
Dear {donor_name},

Thank you for your interest in becoming a blood donor with DonorLink.

After reviewing your application, we regret to inform you that we cannot approve your donor registration at this time.

This may be due to:
- Medical eligibility requirements
- Incomplete information
- Other safety considerations

You may reapply after addressing any concerns or contact our support team for more information.

Thank you for your interest in helping save lives.

Best regards,
DonorLink Team
        """
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #dc3545;">DonorLink Application Update</h2>
            <p>Dear {donor_name},</p>
            <p>Thank you for your interest in becoming a blood donor with DonorLink.</p>
            <p>After reviewing your application, we regret to inform you that we cannot approve your donor registration at this time.</p>
            <h3>This may be due to:</h3>
            <ul>
                <li>Medical eligibility requirements</li>
                <li>Incomplete information</li>
                <li>Other safety considerations</li>
            </ul>
            <p>You may reapply after addressing any concerns or contact our support team for more information.</p>
            <p>Thank you for your interest in helping save lives.</p>
            <p style="color: #dc3545;"><strong>DonorLink Team</strong></p>
        </div>
        """
    
    return send_email(subject, donor_email, body, html_body)

def send_blood_request_notification(donor_email, donor_name, request_details):
    """
    Send blood request notification to compatible donors
    """
    subject = f"Blood Donation Request - {request_details['blood_type']} Needed"
    body = f"""
Dear {donor_name},

We have a blood donation request that matches your blood type.

Request Details:
- Patient: {request_details['patient_name']}
- Blood Type: {request_details['blood_type']}
- Units Needed: {request_details['units_needed']}
- Urgency: {request_details['urgency'].upper()}
- Hospital: {request_details['hospital']}
- Contact: {request_details['contact_phone']}

Your contribution can make a life-saving difference. Please contact the hospital directly if you are available to donate.

Thank you for being a life-saver!

Best regards,
DonorLink Team
    """
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #dc3545;">Blood Donation Request</h2>
        <p>Dear {donor_name},</p>
        <p><strong>We have a blood donation request that matches your blood type.</strong></p>
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
            <h3>Request Details:</h3>
            <ul style="list-style: none; padding: 0;">
                <li><strong>Patient:</strong> {request_details['patient_name']}</li>
                <li><strong>Blood Type:</strong> {request_details['blood_type']}</li>
                <li><strong>Units Needed:</strong> {request_details['units_needed']}</li>
                <li><strong>Urgency:</strong> <span style="color: #dc3545;">{request_details['urgency'].upper()}</span></li>
                <li><strong>Hospital:</strong> {request_details['hospital']}</li>
                <li><strong>Contact:</strong> {request_details['contact_phone']}</li>
            </ul>
        </div>
        <p>Your contribution can make a life-saving difference. Please contact the hospital directly if you are available to donate.</p>
        <p><strong>Thank you for being a life-saver!</strong></p>
        <p style="color: #dc3545;"><strong>DonorLink Team</strong></p>
    </div>
    """
    
    return send_email(subject, donor_email, body, html_body)

def send_request_status_update(user_email, user_name, request_details, new_status):
    """
    Send blood request status update notification
    """
    status_messages = {
        'approved': 'Your blood request has been approved and we are finding compatible donors.',
        'fulfilled': 'Great news! Your blood request has been fulfilled.',
        'cancelled': 'Your blood request has been cancelled.'
    }
    
    subject = f"Blood Request Update - {new_status.title()}"
    body = f"""
Dear {user_name},

{status_messages.get(new_status, 'Your blood request status has been updated.')}

Request Details:
- Patient: {request_details['patient_name']}
- Blood Type: {request_details['blood_type']}
- Units Needed: {request_details['units_needed']}
- Hospital: {request_details['hospital']}
- Status: {new_status.upper()}

If you have any questions, please contact our support team.

Best regards,
DonorLink Team
    """
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #dc3545;">Blood Request Update</h2>
        <p>Dear {user_name},</p>
        <p><strong>{status_messages.get(new_status, 'Your blood request status has been updated.')}</strong></p>
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
            <h3>Request Details:</h3>
            <ul style="list-style: none; padding: 0;">
                <li><strong>Patient:</strong> {request_details['patient_name']}</li>
                <li><strong>Blood Type:</strong> {request_details['blood_type']}</li>
                <li><strong>Units Needed:</strong> {request_details['units_needed']}</li>
                <li><strong>Hospital:</strong> {request_details['hospital']}</li>
                <li><strong>Status:</strong> <span style="color: #dc3545;">{new_status.upper()}</span></li>
            </ul>
        </div>
        <p>If you have any questions, please contact our support team.</p>
        <p style="color: #dc3545;"><strong>DonorLink Team</strong></p>
    </div>
    """
    
    return send_email(subject, user_email, body, html_body)
