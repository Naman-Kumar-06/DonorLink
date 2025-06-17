#!/usr/bin/env python3
"""
Test script to identify import issues
"""
import sys
import time

print("Testing imports...")

try:
    print("1. Importing app...")
    from app import app
    print("   ✓ App imported successfully")
    
    print("2. Importing models...")
    from models import initialize_default_data
    print("   ✓ Models imported successfully")
    
    print("3. Importing utils...")
    from utils import find_compatible_donors
    print("   ✓ Utils imported successfully")
    
    print("4. Importing email_service...")
    from email_service import send_email
    print("   ✓ Email service imported successfully")
    
    print("5. Initializing default data...")
    initialize_default_data()
    print("   ✓ Default data initialized")
    
    print("6. Testing routes import...")
    start_time = time.time()
    import routes
    end_time = time.time()
    print(f"   ✓ Routes imported successfully in {end_time - start_time:.2f} seconds")
    
    print("\nAll imports successful!")
    
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()