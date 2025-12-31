import re
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

def validate_resume_text(resume_text: str) -> Dict[str, Any]:
    """
    Validate the resume text input.
    Returns a dictionary with validation results.
    """
    result = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    if not resume_text:
        result['is_valid'] = False
        result['errors'].append('Resume text is required')
        return result
    
    if not isinstance(resume_text, str):
        result['is_valid'] = False
        result['errors'].append('Resume text must be a string')
        return result
    
    if len(resume_text.strip()) == 0:
        result['is_valid'] = False
        result['errors'].append('Resume text cannot be empty')
        return result
    
    # Check length
    if len(resume_text) > 10000:  # 10k characters max
        result['warnings'].append('Resume text is very long, consider shortening it')
    
    if len(resume_text) < 50:  # Too short
        result['warnings'].append('Resume text seems too short for meaningful analysis')
    
    return result

def sanitize_input(text: str) -> str:
    """
    Sanitize input text by removing potentially harmful content.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove potential script tags
    sanitized = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text, flags=re.IGNORECASE)
    
    # Remove potential iframe tags
    sanitized = re.sub(r'<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>', '', sanitized, flags=re.IGNORECASE)
    
    # Remove potential javascript: urls
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized

def format_response(data: Dict[str, Any], success: bool = True, message: str = "") -> Dict[str, Any]:
    """
    Standardize API response format.
    """
    response = {
        'success': success,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if message:
        response['message'] = message
    
    return response

def calculate_text_metrics(text: str) -> Dict[str, int]:
    """
    Calculate various text metrics for analysis.
    """
    if not text:
        return {
            'char_count': 0,
            'word_count': 0,
            'sentence_count': 0,
            'paragraph_count': 0
        }
    
    # Character count
    char_count = len(text)
    
    # Word count
    words = text.split()
    word_count = len(words)
    
    # Sentence count (approximate)
    import re
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Paragraph count
    paragraphs = text.split('\n\n')
    paragraph_count = len([p for p in paragraphs if p.strip()])
    
    return {
        'char_count': char_count,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'paragraph_count': paragraph_count
    }

def get_experience_from_years(years: int) -> str:
    """
    Convert years of experience to experience level.
    """
    if years >= 10:
        return "Senior"
    elif years >= 5:
        return "Mid-Level"
    elif years >= 2:
        return "Junior"
    else:
        return "Entry Level"

def normalize_job_category(category: str) -> str:
    """
    Normalize job category names to standard format.
    """
    if not category:
        return "Unspecified"
    
    # Common mappings to normalize categories
    category_map = {
        'software engineer': 'Software Engineering',
        'data scientist': 'Data Science',
        'product manager': 'Product Management',
        'project manager': 'Project Management',
        'ui/ux designer': 'UI/UX Design',
        'business analyst': 'Business Analysis',
        'marketing specialist': 'Marketing',
        'sales representative': 'Sales',
        'hr specialist': 'Human Resources',
        'financial analyst': 'Finance',
        'devops engineer': 'DevOps/Infrastructure',
        'full stack developer': 'Software Engineering',
        'frontend developer': 'Software Engineering',
        'backend developer': 'Software Engineering',
        'mobile developer': 'Software Engineering',
        'machine learning engineer': 'Data Science',
        'research scientist': 'Research',
        'technical writer': 'Technical Writing',
        'quality assurance': 'Quality Assurance',
        'cybersecurity specialist': 'Cybersecurity'
    }
    
    normalized = category_map.get(category.lower(), category)
    return normalized.title()

def hash_resume_text(resume_text: str) -> str:
    """
    Create a hash of the resume text for deduplication purposes.
    """
    import hashlib
    return hashlib.sha256(resume_text.encode()).hexdigest()