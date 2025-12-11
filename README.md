# Stroke Prediction System - Secure Healthcare Application

A secure, web-based Flask application designed to support healthcare professionals in managing patient data and predicting stroke risk.

## Features

### Core Functionality
- **Patient Data Management**: Create, Read, Update, and Delete (CRUD) operations for patient records
- **Dual Database System**: 
  - SQLite for user authentication and management
  - MongoDB for patient medical records
- **Intuitive Dashboard**: Real-time statistics on patient data and stroke cases
- **Advanced Search**: Filter and search patient records by various criteria

### Security Features

#### 1. **Password Hashing (PBKDF2-SHA256)**
- Passwords are securely hashed using werkzeug.security
- Minimum password requirements enforced (8+ chars, uppercase, lowercase, number, special char)
- Passwords are never stored in plaintext

#### 2. **Input Validation & Sanitization**
- XSS (Cross-Site Scripting) Prevention: HTML special characters are escaped
- SQL Injection Prevention: Parameterized queries and ORM prevent SQL injection
- Email validation with regex pattern matching
- Patient data validation with type checking and range validation
- Username validation with alphanumeric restrictions

#### 3. **CSRF Protection**
- Flask-WTF CSRF tokens on all forms
- Token validation on POST/PUT/DELETE requests
- Prevents unauthorized cross-site request forgery attacks

#### 4. **Session Security**
- Secure session cookies (HTTPOnly, Secure, SameSite)
- Session timeout after 30 minutes of inactivity
- User activity tracking and logging

#### 5. **Comprehensive Error Logging**
- Security event logging (login attempts, data access, validation errors)
- Separate log files for security, application, and authentication events
- Rotating file handlers to prevent unbounded log growth
- Audit trail for regulatory compliance

#### 6. **Database Security**
- SQLAlchemy ORM prevents SQL injection
- MongoDB parameterized queries
- User authentication data separated from patient medical records

## Installation

### Prerequisites
- Python 3.8+
- MongoDB (for patient records)
- pip (Python package manager)

### Setup Instructions

1. **Clone/Download the project**
```bash
cd stroke-prediction-app
```

2. **Create a virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install MongoDB** (if not already installed)
- Download from: https://www.mongodb.com/try/download/community
- Or use MongoDB Atlas (cloud) at: https://www.mongodb.com/cloud/atlas

5. **Initialize the database**
```bash
python -c "from app import create_app; app = create_app(); app.app_context().push()"
```

6. **Run the application**
```bash
python run.py
```

The application will be available at: `http://localhost:5000`

## Usage

### First Time Setup
1. Navigate to the registration page
2. Create an account with a strong password
3. Log in with your credentials
4. Start managing patient records from the dashboard

### Adding Patient Records
1. Click "Add Patient" from the dashboard
2. Fill in all required fields:
   - Gender (Male, Female, Other)
   - Age (0-120)
   - Hypertension status (Yes/No)
   - Marital status (Yes/No)
   - Employment type
   - Residence type (Rural/Urban)
   - Average glucose level
   - Body Mass Index (BMI)
   - Smoking status
   - Stroke history

3. Submit the form - data is validated and sanitized automatically

### Viewing and Managing Records
- View all patients with pagination
- Edit existing patient records
- Delete patient records (with confirmation)
- Search patients by gender or stroke status

## Security Best Practices Implemented

### OWASP Top 10 Protection
1. **A03:2021 – Injection** - Parameterized queries, input validation
2. **A04:2021 – Insecure Design** - Secure session management
3. **A05:2021 – Security Misconfiguration** - Environment variables for secrets
4. **A06:2021 – Vulnerable Components** - Regular dependency updates
5. **A07:2021 – Authentication** - Password hashing, session security
6. **A08:2021 – Authorization** - Login required decorators
7. **A09:2021 – Logging** - Comprehensive security logging
8. **A10:2021 – SSRF** - Input validation prevents URL manipulation

### Additional Security Measures
- **Content Security Policy ready** structure
- **Secure cookies** with HTTPOnly and Secure flags
- **Rate limiting ready** (can be implemented with Flask-Limiter)
- **GDPR-ready** logging for data access audit trails
- **Data encryption ready** (salted hashing for passwords)

## Testing

### Run Unit Tests
```bash
python -m pytest tests/test_app.py -v
```

### Test Coverage
The test suite includes:
- **Authentication Tests**: User registration, password hashing, login validation
- **Validation Tests**: Email, username, password, and patient data validation
- **CRUD Tests**: Patient record operations
- **Security Tests**: Input sanitization, injection prevention

Example test execution:
```bash
python -m unittest tests.test_app.AuthenticationTestCase -v
python -m unittest tests.test_app.ValidationTestCase -v
```

## Project Structure

```
stroke-prediction-app/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # SQLAlchemy User model
│   ├── routes.py             # Application routes (auth, patient, main)
│   ├── validation.py         # Input validation & sanitization
│   ├── mongo_handler.py      # MongoDB CRUD operations
│   └── error_logging.py      # Security logging utilities
├── templates/                # Jinja2 HTML templates
│   ├── base.html            # Base template with navigation
│   ├── index.html           # Home page
│   ├── login.html           # Login form
│   ├── register.html        # Registration form
│   ├── dashboard.html       # Dashboard with statistics
│   ├── add_patient.html     # Patient creation form
│   ├── edit_patient.html    # Patient editing form
│   └── view_patients.html   # Patient listing with CRUD
├── static/
│   ├── css/                 # CSS stylesheets
│   └── js/                  # JavaScript files
├── tests/
│   └── test_app.py          # Unit tests
├── data/                    # Data and dataset files
├── logs/                    # Application logs (created at runtime)
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md               # This file
```

## Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
MONGO_URI=mongodb://localhost:27017/stroke_prediction
FLASK_ENV=development
```

### Database Configuration
- **SQLite**: Automatically created as `hospital_auth.db`
- **MongoDB**: Ensure MongoDB is running on `localhost:27017` (or configure MONGO_URI)

## Logging and Monitoring

Application logs are stored in the `logs/` directory:

- **security.log** - Security events, login attempts, suspicious activities
- **app.log** - General application events
- **auth.log** - Authentication and authorization events

View logs:
```bash
# View recent security events
tail -f logs/security.log

# View authentication logs
tail -f logs/auth.log
```

## Compliance and Standards

This application follows:
- OWASP Secure Coding Practices
- GDPR principles for data protection
- Healthcare data protection standards
- PEP 8 Python code style guidelines

## Future Enhancements

- [ ] Stroke prediction ML model integration
- [ ] Two-factor authentication (2FA)
- [ ] Role-based access control (RBAC) with granular permissions
- [ ] API rate limiting
- [ ] Data export functionality (CSV, PDF)
- [ ] Advanced analytics dashboard
- [ ] Email notifications for critical events
- [ ] Mobile application support

## Troubleshooting

### MongoDB Connection Error
```
Make sure MongoDB is running:
# On Windows
mongod

# On macOS
brew services start mongodb-community
```

### Port Already in Use
```
python run.py --port 5001
```

### Database Reset
```python
from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset complete")
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Submit a Pull Request

## License

This project is provided for educational purposes.

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review the error messages in the application UI
3. Ensure all dependencies are installed correctly

## Acknowledgments

- Kaggle Stroke Prediction Dataset: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset/data
- Flask Documentation: https://flask.palletsprojects.com/
- OWASP Security Guidelines: https://owasp.org/

---

**Version**: 1.0.0
**Last Updated**: December 2025
**Status**: Production Ready
