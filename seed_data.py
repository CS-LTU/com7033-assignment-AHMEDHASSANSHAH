"""
Script to seed initial test data for the application
Run this after setting up the database
"""
import os
import sys
import csv
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, get_mongo_db
from app.models import db, User


def seed_test_users():
    """Create test users for demonstration"""
    app = create_app()
    with app.app_context():
        # Check if users exist
        if User.query.filter_by(username='doctor1').first():
            print("Test users already exist, skipping...")
            return

        # Create test users
        users_data = [
            {
                'username': 'doctor1',
                'email': 'doctor1@hospital.com',
                'full_name': 'Dr. James Smith',
                'role': 'doctor'
            },
            {
                'username': 'doctor2',
                'email': 'doctor2@hospital.com',
                'full_name': 'Dr. Sarah Johnson',
                'role': 'doctor'
            },
            {
                'username': 'admin',
                'email': 'admin@hospital.com',
                'full_name': 'Admin User',
                'role': 'admin'
            }
        ]

        for user_data in users_data:
            user = User(**user_data)
            user.set_password('TestPassword123!')  # Default password for testing
            db.session.add(user)
            print(f"Created user: {user_data['username']}")

        db.session.commit()
        print(f"✓ Created {len(users_data)} test users")


def seed_sample_patients():
    """Load sample patient data into MongoDB"""
    mongo_db = get_mongo_db()

    if not mongo_db or not mongo_db.patients_collection:
        print("MongoDB is not connected. Ensure MongoDB service is running.")
        return

    # Check if patients exist
    existing = mongo_db.patients_collection.count_documents({})
    if existing > 0:
        print(f"Database already contains {existing} patients, skipping seed...")
        return

    # Sample patient data
    sample_patients = [
        {
            'gender': 'Male',
            'age': 67,
            'hypertension': 1,
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': 228.69,
            'bmi': 36.6,
            'smoking_status': 'formerly smoked',
            'stroke': 1
        },
        {
            'gender': 'Female',
            'age': 61,
            'hypertension': 1,
            'ever_married': 'Yes',
            'work_type': 'Self-employed',
            'Residence_type': 'Rural',
            'avg_glucose_level': 202.21,
            'bmi': 0,
            'smoking_status': 'unknown',
            'stroke': 1
        },
        {
            'gender': 'Male',
            'age': 80,
            'hypertension': 1,
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Rural',
            'avg_glucose_level': 105.92,
            'bmi': 32.5,
            'smoking_status': 'never smoked',
            'stroke': 1
        },
        {
            'gender': 'Female',
            'age': 49,
            'hypertension': 0,
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': 171.23,
            'bmi': 34.4,
            'smoking_status': 'smokes',
            'stroke': 1
        },
        {
            'gender': 'Male',
            'age': 35,
            'hypertension': 0,
            'ever_married': 'No',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': 95.5,
            'bmi': 28.7,
            'smoking_status': 'never smoked',
            'stroke': 0
        },
        {
            'gender': 'Female',
            'age': 28,
            'hypertension': 0,
            'ever_married': 'Yes',
            'work_type': 'Govt_job',
            'Residence_type': 'Rural',
            'avg_glucose_level': 88.9,
            'bmi': 22.1,
            'smoking_status': 'never smoked',
            'stroke': 0
        },
        {
            'gender': 'Male',
            'age': 45,
            'hypertension': 1,
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': 125.3,
            'bmi': 30.5,
            'smoking_status': 'formerly smoked',
            'stroke': 0
        },
        {
            'gender': 'Female',
            'age': 72,
            'hypertension': 1,
            'ever_married': 'Yes',
            'work_type': 'Never_worked',
            'Residence_type': 'Urban',
            'avg_glucose_level': 180.4,
            'bmi': 35.2,
            'smoking_status': 'never smoked',
            'stroke': 1
        },
    ]

    # Insert patients
    for patient in sample_patients:
        mongo_db.create_patient(patient)

    print(f"✓ Seeded {len(sample_patients)} sample patients into MongoDB")


if __name__ == '__main__':
    print("=" * 50)
    print("Database Seeding Script")
    print("=" * 50)

    try:
        print("\n1. Creating test users (SQLite)...")
        seed_test_users()

        print("\n2. Loading sample patient data (MongoDB)...")
        seed_sample_patients()

        print("\n" + "=" * 50)
        print("✓ Seeding complete!")
        print("=" * 50)
        print("\nTest Users:")
        print("  - Username: doctor1 / Password: TestPassword123!")
        print("  - Username: doctor2 / Password: TestPassword123!")
        print("  - Username: admin / Password: TestPassword123!")
        print("\nYou can now log in and view the sample patients.")

    except Exception as e:
        print(f"\n✗ Error during seeding: {str(e)}")
        sys.exit(1)
