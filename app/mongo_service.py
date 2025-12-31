import os
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import gridfs

logger = logging.getLogger(__name__)

class MongoService:
    """
    Service class to handle MongoDB operations for the resume analyzer.
    Supports both cloud (MongoDB Atlas) and local MongoDB instances.
    """
    
    def __init__(self):
        # Get MongoDB connection details from environment variables
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('DB_NAME', 'resume_ai_db')
        
        try:
            # Initialize MongoDB client
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                socketTimeoutMS=20000           # 20 second socket timeout
            )
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
            # Initialize database
            self.db = self.client[self.db_name]
            
            # Initialize collections
            self.users_collection = self.db['users']
            self.resume_analysis_logs = self.db['resume_analysis_logs']
            self.feedback_collection = self.db['feedback']
            
            # Create indexes for better performance
            self._create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Error initializing MongoDB service: {e}")
            raise
    
    def _create_indexes(self):
        """
        Create indexes for better query performance.
        """
        try:
            # Indexes for resume_analysis_logs
            self.resume_analysis_logs.create_index('resume_id')
            self.resume_analysis_logs.create_index('timestamp')
            self.resume_analysis_logs.create_index('resume_text_hash')
            self.resume_analysis_logs.create_index('predicted_category')
            
            # Indexes for users
            self.users_collection.create_index('user_id', unique=True)
            self.users_collection.create_index('email', unique=True)
            
            # Indexes for feedback
            self.feedback_collection.create_index('resume_id')
            self.feedback_collection.create_index('timestamp')
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating MongoDB indexes: {e}")
    
    def store_analysis_result(self, resume_text: str, analysis_result: Dict[str, Any], 
                            device_type: str = 'web') -> str:
        """
        Store the resume analysis result in MongoDB.
        """
        try:
            # Create a hash of the resume text for deduplication
            resume_text_hash = hashlib.sha256(resume_text.encode()).hexdigest()
            
            # Generate a unique resume ID
            resume_id = f"resume_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(resume_text_hash.encode()).hexdigest()[:8]}"
            
            # Prepare the document to store
            document = {
                'resume_id': resume_id,
                'resume_text_hash': resume_text_hash,
                'resume_text_preview': resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,  # Store only preview
                'predicted_category': analysis_result.get('job_category', ''),
                'confidence': analysis_result.get('confidence', 0.0),
                'skills_detected': analysis_result.get('skills', []),
                'experience_level': analysis_result.get('experience_level', ''),
                'summary': analysis_result.get('summary', ''),
                'analysis_details': {
                    'word_count': analysis_result.get('word_count', 0),
                    'character_count': analysis_result.get('character_count', 0),
                    'avg_sentence_length': analysis_result.get('avg_sentence_length', 0.0),
                    'sections': analysis_result.get('sections', []),
                    'keywords': analysis_result.get('keywords', []),
                    'readability_score': analysis_result.get('readability_score', 0.0)
                },
                'device': device_type,
                'timestamp': analysis_result.get('timestamp', datetime.utcnow().isoformat() + 'Z'),
                'created_at': datetime.utcnow()
            }
            
            # Insert the document
            result = self.resume_analysis_logs.insert_one(document)
            
            logger.info(f"Analysis result stored with ID: {resume_id}")
            return resume_id
            
        except Exception as e:
            logger.error(f"Error storing analysis result: {e}")
            raise
    
    def get_analysis_history(self, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch previous resume analysis results.
        """
        try:
            # Query the resume_analysis_logs collection
            cursor = self.resume_analysis_logs.find().sort('created_at', -1).skip(skip).limit(limit)
            results = list(cursor)
            
            # Remove the MongoDB _id field from results for cleaner output
            for result in results:
                if '_id' in result:
                    del result['_id']
            
            logger.info(f"Retrieved {len(results)} analysis records")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching analysis history: {e}")
            raise
    
    def get_analysis_by_id(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific analysis result by resume ID.
        """
        try:
            result = self.resume_analysis_logs.find_one({'resume_id': resume_id})
            
            if result and '_id' in result:
                del result['_id']
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching analysis by ID: {e}")
            raise
    
    def store_user(self, user_data: Dict[str, Any]) -> str:
        """
        Store user information in the database.
        """
        try:
            # Generate user ID if not provided
            if 'user_id' not in user_data:
                user_data['user_id'] = f"user_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            user_data['created_at'] = datetime.utcnow()
            
            result = self.users_collection.insert_one(user_data)
            logger.info(f"User stored with ID: {user_data['user_id']}")
            
            return user_data['user_id']
            
        except Exception as e:
            logger.error(f"Error storing user: {e}")
            raise
    
    def store_feedback(self, resume_id: str, feedback_data: Dict[str, Any]) -> str:
        """
        Store user feedback for a specific analysis.
        """
        try:
            feedback_doc = {
                'resume_id': resume_id,
                'feedback': feedback_data,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'created_at': datetime.utcnow()
            }
            
            result = self.feedback_collection.insert_one(feedback_doc)
            logger.info(f"Feedback stored for resume ID: {resume_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing feedback: {e}")
            raise
    
    def close_connection(self):
        """
        Close the MongoDB connection.
        """
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
    
    def health_check(self) -> bool:
        """
        Perform a health check on the MongoDB connection.
        """
        try:
            # Ping the database
            self.client.admin.command('ping')
            return True
        except Exception:
            return False


# Global instance
mongo_service = MongoService()