# DonorLink - Blood Donation Management System

A comprehensive web-based blood donation management system that connects blood donors with patients in need. Built with Flask, Bootstrap, and modern web technologies.

## Features

### Core Functionality
- **User Registration & Authentication**: Secure user registration with session-based authentication
- **Role-Based Access Control**: Separate interfaces for regular users and administrators
- **Donor Registration**: Complete donor profile management with blood type and availability tracking
- **Blood Request System**: Patients can submit blood requests with urgency levels and location
- **Smart Matching**: Automatic compatibility matching between donors and blood requests
- **Email Notifications**: Automated email alerts for approvals, rejections, and matches

### Enhanced Admin Features
- **Real-Time Analytics Dashboard**: Comprehensive statistics with interactive charts
- **Blood Inventory Management**: Track blood bank inventory with expiry monitoring
- **Critical Stock Alerts**: Automatic alerts for low blood inventory levels
- **Interactive Charts**: Visual analytics using Chart.js for data visualization
- **Approval Workflow**: Streamlined donor approval and blood request management

### Authentication Options
- **Traditional Login**: Email and password authentication
- **Firebase Integration**: Google Sign-In support with Firebase authentication
- **Session Management**: Secure session handling with role-based access

### Technical Features
- **Responsive Design**: Mobile-first Bootstrap 5 interface
- **Database Flexibility**: Supports both cloud MySQL (FreeSQLDatabase.com) and in-memory storage
- **API Endpoints**: RESTful APIs for analytics and inventory management
- **Thread-Safe Operations**: Concurrent user support with proper locking mechanisms
- **Email Integration**: SMTP-based email notifications

## System Requirements

### Local Development
- **Python**: 3.11 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 512MB RAM
- **Storage**: 100MB free space

### Dependencies
- Flask 3.0+
- Werkzeug (security utilities)
- Gunicorn (production server)
- PyMySQL (MySQL database connector)
- Email-validator
- Cryptography
- PyreBase4 (Firebase integration)

## Installation & Setup

### 1. Clone or Download
```bash
# If using Git
git clone git clone https://github.com/Naman-Kumar-06/DonorLink.git
cd donorlink

# Or download and extract the project files
```

### 2. Install Python Dependencies
```bash
# Install required packages
pip install flask werkzeug gunicorn pymysql email-validator cryptography pyrebase4

# Or if you have the requirements file
pip install -r pyproject.toml
```

### 3. Environment Configuration
Create a `.env` file in the project root:

```env
# Required - Session Security
SESSION_SECRET=your_random_secret_key_here

# Optional - Email Configuration (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Optional - Cloud Database (FreeSQLDatabase.com)
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name

# Optional - Firebase Authentication
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_APP_ID=your_firebase_app_id
```

### 4. Database Setup

#### Option A: In-Memory Storage (Default)
No additional setup required. Data will be stored in memory during runtime.

#### Option B: Cloud MySQL Database
1. Sign up at [FreeSQLDatabase.com](https://www.freesqldatabase.com/)
2. Create a new database
3. Add your database credentials to the `.env` file
4. The system will automatically create required tables

### 5. Email Configuration (Optional)
For Gmail SMTP:
1. Enable 2-factor authentication on your Google account
2. Generate an app-specific password
3. Use your Gmail address and app password in the `.env` file

### 6. Firebase Setup (Optional)
For Google Sign-In functionality:
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Add a web app to your project
4. Enable Authentication > Sign-in method > Google
5. Add your domain to authorized domains
6. Copy the configuration values to your `.env` file

## Running the Application

### Development Mode
```bash
# Run with Flask development server
python app.py

# Or use the main entry point
python main.py
```

### Production Mode
```bash
# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

# For multiple workers
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

### Access the Application
- **Local**: http://localhost:5000
- **Network**: http://your-ip-address:5000

## Default Admin Account

The system creates a default administrator account:
- **Email**: admin@donorlink.com
- **Password**: admin123
- **Role**: Administrator

**Important**: Change the default admin password after first login.

## User Guide

### For Regular Users
1. **Registration**: Create an account with email and password
2. **Donor Registration**: Complete your donor profile with blood type and availability
3. **Blood Requests**: Submit requests when you need blood
4. **Dashboard**: Track your donations and requests
5. **Notifications**: Receive email updates on application status

### For Administrators
1. **Admin Dashboard**: Access comprehensive analytics and management tools
2. **Donor Management**: Approve or reject donor applications
3. **Request Management**: Manage blood requests and find matches
4. **Inventory Management**: Track blood bank inventory and expiry dates
5. **Analytics**: View real-time statistics and charts
6. **Critical Alerts**: Monitor low stock levels and urgent requests

## Project Structure

```
DonorLink
│
├── __pycache__/                     # Python bytecode cache folder
│
├── static/                          # Static files like CSS & JavaScript
│   ├── css/
│   │   └── style.css                # Stylesheet for frontend UI
│   │
│   └── js/
│       ├── charts.js                # Chart rendering (e.g., blood inventory)
│       └── main.js                  # Main frontend JS logic
│
├── templates/                       # HTML templates rendered by Flask
│   ├── 404.html                     # Page not found error
│   ├── 500.html                     # Internal server error
│   ├── base.html                    # Base layout template
│   ├── index.html                   # Landing page
│   ├── login.html                   # Firebase login form
│   ├── register.html                # Firebase signup form
│   ├── dashboard.html               # User dashboard
│   ├── profile.html                 # User profile view/update
│   ├── donor_registration.html      # Donor form for users
│   ├── blood_request.html           # Blood request form for users
│   │
│   ├── admin_dashboard.html         # Admin main dashboard
│   ├── admin_donors.html            # View/approve donors
│   ├── admin_requests.html          # View/manage blood requests
│   └── admin_inventory.html         # Blood stock visualization
│
├── .env                             # Environment variables (Firebase, DB creds)
├── app.py                           # Flask app initializer
├── main.py                          # App runner or logic handler
├── email_service.py                 # Handles sending emails (SMTP, etc.)
├── models.py                        # Database models and ORM logic
├── routes.py                        # URL route handling for user/admin
├── utils.py                         # Helper functions (decorators, validators)
│
├── simple_app.py                    # Minimal Flask app (possibly test/starter)
├── test_import.py                   # Python import testing script
├── test_minimal.py                  # Minimal functionality test script
│
├── pyproject.toml                   # Python project metadata and dependencies
├── uv.lock                          # Package lock file for `uv` environment
│
├── README.md                        # Project overview and instructions

```

## API Endpoints

### Analytics APIs
- `GET /api/analytics` - Dashboard analytics data
- `GET /api/blood_inventory` - Blood inventory information
- `POST /api/update_inventory` - Update inventory levels



## Configuration Options

### Database Configuration
The system supports multiple database backends:
- **In-Memory**: Default, data persists during runtime only
- **Cloud MySQL**: Production-ready with FreeSQLDatabase.com
- **Local MySQL**: Can be configured for local development

### Email Configuration
Supports SMTP email providers:
- **Gmail**: Recommended for development and small deployments
- **Custom SMTP**: Any SMTP server can be configured

### Authentication Methods
- **Session-based**: Default Flask session management
- **Firebase**: Google Sign-In integration
- **Both**: Users can choose their preferred method

## Security Features

- **Password Hashing**: Werkzeug security for password protection
- **Session Management**: Secure session handling with secret keys
- **Role-Based Access**: Admin and user role separation
- **Input Validation**: Form validation and sanitization
- **CSRF Protection**: Built-in Flask security features

## Performance Optimization

- **Thread-Safe Operations**: Supports concurrent users
- **Efficient Queries**: Optimized database operations
- **Caching**: Session-based data caching
- **Responsive Design**: Mobile-optimized interface
- **Asset Optimization**: Minimized CSS and JavaScript

## Troubleshooting

### Common Issues

1. **Application won't start**
   - Check Python version (3.11+ required)
   - Verify all dependencies are installed
   - Ensure SESSION_SECRET is set in environment

2. **Database connection issues**
   - Verify database credentials in `.env` file
   - Check network connectivity to database server
   - Ensure database exists and is accessible

3. **Email notifications not working**
   - Verify SMTP configuration in `.env` file
   - Check email provider settings
   - Ensure app-specific passwords for Gmail

4. **Firebase authentication issues**
   - Verify Firebase configuration
   - Check authorized domains in Firebase console
   - Ensure API keys are correct

### Debug Mode
Enable debug logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support and questions:
- Check this README for common solutions
- Review the troubleshooting section
- Ensure all environment variables are correctly configured

## Version History

- **v1.0.0** (May 2025): Initial release with core functionality
- **v1.1.0** (June 2025): Added user and admin based specific functionality
- **v1.2.0** (June 2025): Added blood inventory management and analytics

---
