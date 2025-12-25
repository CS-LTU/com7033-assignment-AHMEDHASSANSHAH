"""
MongoDB database handler for patient records
"""
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MongoDBHandler:
    def __init__(self, uri: str = None):
        """Initialize MongoDB connection"""
        self.uri = uri or 'mongodb://localhost:27017/stroke_prediction'
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client['stroke_prediction']
            self.patients_collection = self.db['patients']
            # Test connection
            self.client.admin.command('ping')
            logger.info("MongoDB connected successfully")
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self.client = None
            self.db = None
            self.patients_collection = None

    def count_patients(self) -> int:
        """
        Return the total number of patients in the collection.
        """
        try:
            return self.patients_collection.count_documents({})
        except Exception as e:
            logger.error(f"Error counting patients: {str(e)}")
            return 0

    def create_patient(self, patient_data: dict) -> dict:
        """
        Create a new patient record.
        Adds timestamp and sequential ID automatically.
        """
        try:
            # Generate a sequential ID
            last_patient = self.patients_collection.find_one(sort=[('id', -1)])
            next_id = (last_patient.get('id', 0) if last_patient else 0) + 1
            patient_data['id'] = next_id
            patient_data['created_at'] = datetime.utcnow()
            patient_data['updated_at'] = datetime.utcnow()
            result = self.patients_collection.insert_one(patient_data)
            logger.info(f"Patient created with MongoDB ID: {result.inserted_id} and Patient ID: {next_id}")
            return {'success': True, 'id': str(result.inserted_id)}
        except PyMongoError as e:
            logger.error(f"Error creating patient: {str(e)}")
            return {'success': False, 'error': str(e)}

    def read_patient(self, patient_id: str) -> dict:
        """
        Read a single patient record by ID.
        """
        try:
            patient = self.patients_collection.find_one({'_id': ObjectId(patient_id)})
            if patient:
                patient['_id'] = str(patient['_id'])
                return {'success': True, 'data': patient}
            return {'success': False, 'error': 'Patient not found'}
        except Exception as e:
            logger.error(f"Error reading patient: {str(e)}")
            return {'success': False, 'error': str(e)}

    def read_all_patients(self, limit: int = 100, skip: int = 0) -> dict:
        """
        Read all patient records with pagination.
        """
        try:
            patients = list(self.patients_collection.find().skip(skip).limit(limit))
            for patient in patients:
                patient['_id'] = str(patient['_id'])
            return {'success': True, 'data': patients, 'count': len(patients)}
        except PyMongoError as e:
            logger.error(f"Error reading patients: {str(e)}")
            return {'success': False, 'error': str(e)}

    def update_patient(self, patient_id: str, update_data: dict) -> dict:
        """
        Update a patient record.
        Updates the updated_at timestamp automatically.
        """
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.patients_collection.update_one(
                {'_id': ObjectId(patient_id)},
                {'$set': update_data}
            )
            if result.matched_count > 0:
                logger.info(f"Patient {patient_id} updated successfully")
                return {'success': True, 'message': 'Patient updated'}
            return {'success': False, 'error': 'Patient not found'}
        except Exception as e:
            logger.error(f"Error updating patient: {str(e)}")
            return {'success': False, 'error': str(e)}

    def delete_patient(self, patient_id: str) -> dict:
        """
        Delete a patient record.
        """
        try:
            result = self.patients_collection.delete_one({'_id': ObjectId(patient_id)})
            if result.deleted_count > 0:
                logger.info(f"Patient {patient_id} deleted successfully")
                return {'success': True, 'message': 'Patient deleted'}
            return {'success': False, 'error': 'Patient not found'}
        except Exception as e:
            logger.error(f"Error deleting patient: {str(e)}")
            return {'success': False, 'error': str(e)}

    def search_patients(self, query: dict, limit: int = 50) -> dict:
        """
        Search patients by multiple criteria.
        Supports filtering by gender, age range, stroke status, etc.
        """
        try:
            patients = list(self.patients_collection.find(query).limit(limit))
            for patient in patients:
                patient['_id'] = str(patient['_id'])
            return {'success': True, 'data': patients, 'count': len(patients)}
        except PyMongoError as e:
            logger.error(f"Error searching patients: {str(e)}")
            return {'success': False, 'error': str(e)}

    def search_patient_by_id(self, patient_id: str) -> dict:
        """
        Search for a patient by their sequential ID field.
        """
        try:
            patient = self.patients_collection.find_one({'id': int(patient_id)})
            if patient:
                patient['_id'] = str(patient['_id'])
                return {'success': True, 'data': patient}
            return {'success': False, 'error': 'Patient not found'}
        except Exception as e:
            logger.error(f"Error searching patient by id: {str(e)}")
            return {'success': False, 'error': str(e)}

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

def update_patient(self, patient_id: str, update_data: dict) -> dict:
        """
        Update a patient record.
        Updates the updated_at timestamp automatically.
        """
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.patients_collection.update_one(
                {'_id': ObjectId(patient_id)},
                {'$set': update_data}
            )
            if result.matched_count > 0:
                logger.info(f"Patient {patient_id} updated successfully")
                return {'success': True, 'message': 'Patient updated'}
            return {'success': False, 'error': 'Patient not found'}
        except Exception as e:
            logger.error(f"Error updating patient: {str(e)}")
            return {'success': False, 'error': str(e)}

def delete_patient(self, patient_id: str) -> dict:
        """
        Delete a patient record.
        """
        try:
            result = self.patients_collection.delete_one({'_id': ObjectId(patient_id)})
            if result.deleted_count > 0:
                logger.info(f"Patient {patient_id} deleted successfully")
                return {'success': True, 'message': 'Patient deleted'}
            return {'success': False, 'error': 'Patient not found'}
        except Exception as e:
            logger.error(f"Error deleting patient: {str(e)}")
            return {'success': False, 'error': str(e)}

def search_patients(self, query: dict, limit: int = 50) -> dict:
        """
        Search patients by multiple criteria.
        Supports filtering by gender, age range, stroke status, etc.
        """
        try:
            patients = list(self.patients_collection.find(query).limit(limit))
            for patient in patients:
                patient['_id'] = str(patient['_id'])
            return {'success': True, 'data': patients, 'count': len(patients)}
        except PyMongoError as e:
            logger.error(f"Error searching patients: {str(e)}")
            return {'success': False, 'error': str(e)}

def search_patient_by_id(self, patient_id: str) -> dict:
        """
        Search for a patient by their sequential ID field.
        """
        try:
            patient = self.patients_collection.find_one({'id': int(patient_id)})
            if patient:
                patient['_id'] = str(patient['_id'])
                return {'success': True, 'data': patient}
            return {'success': False, 'error': 'Patient not found'}
        except Exception as e:
            logger.error(f"Error searching patient by id: {str(e)}")
            return {'success': False, 'error': str(e)}

def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
