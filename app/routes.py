"""
Application routes for authentication, patients, and main pages
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf.csrf import generate_csrf
from app.models import db, User
from app.validation import (
    validate_email, validate_username, validate_password,
    validate_patient_data, sanitize_patient_data, sanitize_string, ValidationError
)
from app.error_logging import SecurityLogger
from app import get_mongo_db
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
patient_bp = Blueprint('patient', __name__, url_prefix='/patient')
main_bp = Blueprint('main', __name__)


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_dashboard_stats():
    """
    Helper function to get dashboard statistics.
    Returns a dictionary with total patients, stroke cases, and stroke rate.
    """
    mongo_db = get_mongo_db()
    
    # Get patient statistics
    patients_result = mongo_db.read_all_patients(limit=1000)
    total_patients = patients_result['count'] if patients_result['success'] else 0

    # Count stroke cases
    stroke_count = 0
    if patients_result['success']:
        for patient in patients_result['data']:
            if patient.get('stroke') == 1 or patient.get('stroke') == '1':
                stroke_count += 1

    return {
        'total_patients': total_patients,
        'stroke_cases': stroke_count,
        'stroke_rate': round((stroke_count / total_patients * 100) if total_patients > 0 else 0, 2)
    }


# ==================== AUTHENTICATION ROUTES ====================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    Validates input and hashes passwords before storing.
    SECURITY: Input validation, password hashing, CSRF protection
    """
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            full_name = request.form.get('full_name', '').strip()

            # Input validation
            if not validate_username(username):
                raise ValidationError("Username must be 3-20 characters (alphanumeric, _, -)")
            
            if not validate_email(email):
                raise ValidationError("Invalid email format")
            
            is_valid, message = validate_password(password)
            if not is_valid:
                raise ValidationError(message)

            # Check if user exists
            if User.query.filter_by(username=username).first():
                raise ValidationError("Username already exists")
            if User.query.filter_by(email=email).first():
                raise ValidationError("Email already exists")

            # Create user
            user = User(
                username=sanitize_string(username),
                email=sanitize_string(email),
                full_name=sanitize_string(full_name),
                role='doctor'
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            SecurityLogger.log_login_attempt(username, True)
            flash('Registration successful! Please log in.', 'success')
            logger.info(f"New user registered: {username}")
            return redirect(url_for('auth.login'))

        except ValidationError as e:
            SecurityLogger.log_validation_error('registration', str(e))
            flash(f'Registration error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration', 'danger')

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    Authenticates user and creates secure session.
    SECURITY: Password verification, session handling, login logging
    """
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not username or not password:
                raise ValidationError("Username and password required")

            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password) and user.is_active:
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                session.permanent = True

                # Update last login
                user.last_login = db.func.now()
                db.session.commit()

                SecurityLogger.log_login_attempt(username, True, request.remote_addr)
                logger.info(f"User logged in: {username}")
                flash(f'Welcome back, {user.full_name}!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                SecurityLogger.log_login_attempt(username, False, request.remote_addr)
                flash('Invalid username or password', 'danger')

        except ValidationError as e:
            SecurityLogger.log_validation_error('login', str(e))
            flash(f'Login error: {str(e)}', 'danger')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """User logout route"""
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


# ==================== MAIN ROUTES ====================

@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard - main application page.
    Shows patient statistics and quick actions.
    """
    stats = get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)


# ==================== PATIENT CRUD ROUTES ====================

@patient_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """
    Add new patient route.
    SECURITY: Input validation, data sanitization, CSRF protection
    """
    if request.method == 'POST':
        try:
            patient_data = request.form.to_dict()

            # Validate patient data
            is_valid, message = validate_patient_data(patient_data)
            if not is_valid:
                raise ValidationError(message)

            # Sanitize data
            patient_data = sanitize_patient_data(patient_data)

            # Create patient
            mongo_db = get_mongo_db()
            result = mongo_db.create_patient(patient_data)

            if result['success']:
                SecurityLogger.log_patient_access(session.get('user_id'), result['id'], 'CREATE')
                flash('Patient record created successfully', 'success')
                logger.info(f"Patient created by user {session.get('username')}")
                return redirect(url_for('patient.view_patients'))
            else:
                raise Exception(result.get('error', 'Unknown error'))

        except ValidationError as e:
            SecurityLogger.log_validation_error('patient_data', str(e), session.get('user_id'))
            flash(f'Validation error: {str(e)}', 'danger')
        except Exception as e:
            logger.error(f"Error adding patient: {str(e)}")
            flash(f'Error: {str(e)}', 'danger')

    return render_template('add_patient.html')


@patient_bp.route('/view')
@login_required
def view_patients():
    """
    View all patients with pagination.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        skip = (page - 1) * per_page

        mongo_db = get_mongo_db()
        result = mongo_db.read_all_patients(limit=per_page, skip=skip)
        
        # Calculate total pages
        all_patients = mongo_db.read_all_patients(limit=1000)
        total_patients = all_patients['count'] if all_patients['success'] else 0
        total_pages = (total_patients + per_page - 1) // per_page  # Ceiling division

        if result['success']:
            return render_template('view_patients.html', 
                                 patients=result['data'],
                                 page=page,
                                 total_pages=total_pages)
        else:
            flash('Error retrieving patients', 'danger')
            return render_template('view_patients.html', 
                                 patients=[],
                                 page=page,
                                 total_pages=total_pages)

    except Exception as e:
        logger.error(f"Error viewing patients: {str(e)}")
        flash('An error occurred', 'danger')
        return redirect(url_for('main.dashboard'))


@patient_bp.route('/search-by-id', methods=['POST'])
@login_required
def search_by_id():
    """
    Search for a patient by their ID field (the table ID displayed in patients list).
    SECURITY: Input validation and sanitization
    """
    try:
        patient_id = request.form.get('patient_id', '').strip()
        
        if not patient_id:
            return redirect(url_for('main.dashboard'))
        
        # Sanitize the patient ID
        patient_id = sanitize_string(patient_id)
        
        # Get patient from database by ID field
        mongo_db = get_mongo_db()
        result = mongo_db.search_patient_by_id(patient_id)
        
        if result['success']:
            SecurityLogger.log_patient_access(session.get('user_id'), patient_id, 'READ')
            logger.info(f"Patient {patient_id} accessed by user {session.get('username')}")
            return render_template('dashboard.html', 
                                 patient=result['data'],
                                 stats=get_dashboard_stats())
        else:
            return render_template('dashboard.html',
                                 search_error=f"Patient not found with ID: {patient_id}",
                                 stats=get_dashboard_stats())
    
    except Exception as e:
        logger.error(f"Error searching patient by ID: {str(e)}")
        return render_template('dashboard.html',
                             search_error=f"Error searching patient: {str(e)}",
                             stats=get_dashboard_stats())


@patient_bp.route('/edit/<patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    """
    Edit patient record.
    SECURITY: Input validation, data sanitization, patient access logging
    """
    mongo_db = get_mongo_db()

    if request.method == 'POST':
        try:
            update_data = request.form.to_dict()

            # Validate patient data
            is_valid, message = validate_patient_data(update_data)
            if not is_valid:
                raise ValidationError(message)

            # Sanitize data
            update_data = sanitize_patient_data(update_data)

            # Update patient
            result = mongo_db.update_patient(patient_id, update_data)

            if result['success']:
                SecurityLogger.log_patient_access(session.get('user_id'), patient_id, 'UPDATE')
                flash('Patient record updated successfully', 'success')
                logger.info(f"Patient {patient_id} updated by {session.get('username')}")
                return redirect(url_for('patient.view_patients'))
            else:
                raise Exception(result.get('error', 'Unknown error'))

        except ValidationError as e:
            SecurityLogger.log_validation_error('patient_data', str(e), session.get('user_id'))
            flash(f'Validation error: {str(e)}', 'danger')
        except Exception as e:
            logger.error(f"Error updating patient: {str(e)}")
            flash(f'Error: {str(e)}', 'danger')

    else:
        try:
            result = mongo_db.read_patient(patient_id)
            if result['success']:
                SecurityLogger.log_patient_access(session.get('user_id'), patient_id, 'READ')
                return render_template('edit_patient.html', 
                                     patient=result['data'])
            else:
                flash('Patient not found', 'danger')
                return redirect(url_for('patient.view_patients'))
        except Exception as e:
            logger.error(f"Error retrieving patient: {str(e)}")
            flash('An error occurred', 'danger')
            return redirect(url_for('patient.view_patients'))


@patient_bp.route('/delete/<patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    """
    Delete patient record.
    SECURITY: CSRF protection, access logging, confirmation required
    """
    try:
        mongo_db = get_mongo_db()
        result = mongo_db.delete_patient(patient_id)

        if result['success']:
            SecurityLogger.log_patient_access(session.get('user_id'), patient_id, 'DELETE')
            flash('Patient record deleted successfully', 'success')
            logger.info(f"Patient {patient_id} deleted by {session.get('username')}")
        else:
            flash('Error deleting patient', 'danger')

    except Exception as e:
        logger.error(f"Error deleting patient: {str(e)}")
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('patient.view_patients'))


@patient_bp.route('/search', methods=['GET'])
@login_required
def search_patients():
    """
    Search patients by criteria.
    SECURITY: Input validation and sanitization
    """
    try:
        gender = request.args.get('gender', '').strip()
        stroke = request.args.get('stroke', '').strip()

        query = {}

        if gender:
            query['gender'] = sanitize_string(gender)

        if stroke:
            try:
                query['stroke'] = int(sanitize_string(stroke))
            except ValueError:
                pass

        mongo_db = get_mongo_db()
        result = mongo_db.search_patients(query)

        if result['success']:
            return render_template('search_results.html',
                                 patients=result['data'])
        else:
            flash('Error searching patients', 'danger')

    except Exception as e:
        logger.error(f"Error searching patients: {str(e)}")
        flash('An error occurred', 'danger')

    return redirect(url_for('patient.view_patients'))
