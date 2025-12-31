from flask import Flask, request, jsonify
import os
import logging
from datetime import datetime

# Import our modules
from app.model_loader import model_loader
from app.inference import inference_engine
from app.mongo_service import mongo_service
from app.utils import validate_resume_text, sanitize_input, format_response, hash_resume_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict job category from resume text.
    Expected JSON: {"resume_text": "resume content here"}
    Returns: job category, confidence, skills, experience level, summary
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'resume_text' not in data:
            return jsonify(format_response(
                {}, 
                success=False, 
                message="Missing resume_text in request body"
            )), 400
        
        resume_text = data['resume_text']
        
        # Validate input
        validation_result = validate_resume_text(resume_text)
        if not validation_result['is_valid']:
            return jsonify(format_response(
                {'errors': validation_result['errors']},
                success=False,
                message="Invalid input"
            )), 400
        
        # Sanitize input
        sanitized_text = sanitize_input(resume_text)
        
        # Perform prediction
        prediction_result = inference_engine.predict_job_category(sanitized_text)
        
        # Store result in MongoDB
        device_type = request.headers.get('User-Agent', 'unknown')
        resume_id = mongo_service.store_analysis_result(
            resume_text=sanitized_text,
            analysis_result=prediction_result,
            device_type=device_type
        )
        
        # Add resume ID to the result
        prediction_result['resume_id'] = resume_id
        
        return jsonify(format_response({
            'job_category': prediction_result['job_category'],
            'confidence': prediction_result['confidence'],
            'skills': prediction_result['skills'],
            'experience_level': prediction_result['experience_level'],
            'summary': prediction_result['summary'],
            'timestamp': prediction_result['timestamp'],
            'resume_id': resume_id
        }))
        
    except Exception as e:
        logger.error(f"Error in /predict endpoint: {e}")
        return jsonify(format_response(
            {},
            success=False,
            message=f"Internal server error: {str(e)}"
        )), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Deep analysis of resume text.
    Expected JSON: {"resume_text": "resume content here"}
    Returns: comprehensive analysis including predictions and insights
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'resume_text' not in data:
            return jsonify(format_response(
                {},
                success=False,
                message="Missing resume_text in request body"
            )), 400
        
        resume_text = data['resume_text']
        
        # Validate input
        validation_result = validate_resume_text(resume_text)
        if not validation_result['is_valid']:
            return jsonify(format_response(
                {'errors': validation_result['errors']},
                success=False,
                message="Invalid input"
            )), 400
        
        # Sanitize input
        sanitized_text = sanitize_input(resume_text)
        
        # Perform deep analysis
        analysis_result = inference_engine.analyze_resume(sanitized_text)
        
        # Store result in MongoDB
        device_type = request.headers.get('User-Agent', 'unknown')
        resume_id = mongo_service.store_analysis_result(
            resume_text=sanitized_text,
            analysis_result=analysis_result,
            device_type=device_type
        )
        
        # Add resume ID to the result
        analysis_result['resume_id'] = resume_id
        
        return jsonify(format_response({
            'job_category': analysis_result['job_category'],
            'confidence': analysis_result['confidence'],
            'skills': analysis_result['skills'],
            'experience_level': analysis_result['experience_level'],
            'summary': analysis_result['summary'],
            'word_count': analysis_result['word_count'],
            'character_count': analysis_result['character_count'],
            'avg_sentence_length': analysis_result['avg_sentence_length'],
            'sections': analysis_result['sections'],
            'keywords': analysis_result['keywords'],
            'readability_score': analysis_result['readability_score'],
            'timestamp': analysis_result['timestamp'],
            'resume_id': resume_id
        }))
        
    except Exception as e:
        logger.error(f"Error in /analyze endpoint: {e}")
        return jsonify(format_response(
            {},
            success=False,
            message=f"Internal server error: {str(e)}"
        )), 500


@app.route('/store-result', methods=['POST'])
def store_result():
    """
    Manually store a resume analysis result in MongoDB.
    Expected JSON: {
        "resume_text": "resume content",
        "analysis_result": {...},
        "device_type": "web|mobile"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data or 'analysis_result' not in data:
            return jsonify(format_response(
                {},
                success=False,
                message="Missing required fields: resume_text and analysis_result"
            )), 400
        
        resume_text = data['resume_text']
        analysis_result = data['analysis_result']
        device_type = data.get('device_type', 'web')
        
        # Validate input
        validation_result = validate_resume_text(resume_text)
        if not validation_result['is_valid']:
            return jsonify(format_response(
                {'errors': validation_result['errors']},
                success=False,
                message="Invalid input"
            )), 400
        
        # Sanitize input
        sanitized_text = sanitize_input(resume_text)
        
        # Store result in MongoDB
        resume_id = mongo_service.store_analysis_result(
            resume_text=sanitized_text,
            analysis_result=analysis_result,
            device_type=device_type
        )
        
        return jsonify(format_response({
            'resume_id': resume_id,
            'message': 'Result stored successfully'
        }))
        
    except Exception as e:
        logger.error(f"Error in /store-result endpoint: {e}")
        return jsonify(format_response(
            {},
            success=False,
            message=f"Internal server error: {str(e)}"
        )), 500


@app.route('/history', methods=['GET'])
def history():
    """
    Fetch previous resume analysis results.
    Query params: limit (default 50), skip (default 0)
    """
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Ensure reasonable limits
        limit = min(max(limit, 1), 100)  # Between 1 and 100
        skip = max(skip, 0)
        
        # Fetch history from MongoDB
        history_results = mongo_service.get_analysis_history(limit=limit, skip=skip)
        
        return jsonify(format_response({
            'results': history_results,
            'count': len(history_results),
            'limit': limit,
            'skip': skip
        }))
        
    except ValueError:
        return jsonify(format_response(
            {},
            success=False,
            message="Invalid limit or skip parameters"
        )), 400
    except Exception as e:
        logger.error(f"Error in /history endpoint: {e}")
        return jsonify(format_response(
            {},
            success=False,
            message=f"Internal server error: {str(e)}"
        )), 500


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    Returns service status and model loading status.
    """
    try:
        # Check MongoDB connection
        db_health = mongo_service.health_check()
        
        # Check if models are loaded
        models_loaded = model_loader.is_loaded()
        
        health_status = {
            'status': 'healthy' if (db_health and models_loaded) else 'unhealthy',
            'database_connected': db_health,
            'models_loaded': models_loaded,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return jsonify(format_response(health_status)), status_code
        
    except Exception as e:
        logger.error(f"Error in /health endpoint: {e}")
        return jsonify(format_response(
            {'status': 'unhealthy'},
            success=False,
            message=f"Health check failed: {str(e)}"
        )), 503


@app.route('/version', methods=['GET'])
def version():
    """
    Version information endpoint.
    """
    version_info = {
        'version': '1.0.0',
        'service': 'AI Resume Analyzer API',
        'model_loaded': model_loader.is_loaded(),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    return jsonify(format_response(version_info))


# CORS support
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == '__main__':
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get('PORT', 5000))
    
    # Log startup info
    logger.info(f"Starting AI Resume Analyzer API on port {port}")
    logger.info(f"Models loaded: {model_loader.is_loaded()}")
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)