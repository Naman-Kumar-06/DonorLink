#!/usr/bin/env python3
"""
Minimal test to identify blocking operations
"""
from flask import Flask

# Create minimal Flask app
test_app = Flask(__name__)
test_app.secret_key = "test-key"

@test_app.route('/')
def hello():
    return "Hello World!"

if __name__ == "__main__":
    print("Starting minimal Flask app...")
    test_app.run(host="0.0.0.0", port=5001, debug=True)