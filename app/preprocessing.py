import re
import nltk
import string
import logging
from typing import List, Dict, Any
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

logger = logging.getLogger(__name__)

class ResumePreprocessor:
    """
    Handles preprocessing of resume text for ML model inference.
    """
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def clean_text(self, text: str) -> str:
        """
        Clean the resume text by removing special characters, extra whitespaces, etc.
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters and digits (keep only letters and spaces)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespaces
        text = ' '.join(text.split())
        
        return text
    
    def tokenize_and_process(self, text: str) -> List[str]:
        """
        Tokenize text and perform additional processing like removing stopwords and lemmatization.
        """
        if not text:
            return []
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and punctuation, then lemmatize
        processed_tokens = []
        for token in tokens:
            if (token not in self.stop_words and 
                token not in string.punctuation and 
                len(token) > 2):  # Remove very short tokens
                lemmatized_token = self.lemmatizer.lemmatize(token)
                processed_tokens.append(lemmatized_token)
        
        return processed_tokens
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract potential skills from the resume text.
        This is a simplified implementation - in a real system, this would use 
        a more sophisticated approach with skill dictionaries or NER.
        """
        # Common skills keywords (simplified approach)
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'sql',
            'mongodb', 'postgresql', 'mysql', 'django', 'flask', 'spring', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'machine learning', 'deep learning',
            'data science', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'git',
            'agile', 'scrum', 'project management', 'leadership', 'teamwork', 'communication',
            'problem solving', 'analytical', 'marketing', 'sales', 'design', 'ui/ux',
            'android', 'ios', 'flutter', 'react native', 'php', 'ruby', 'c++', 'c#',
            'html', 'css', 'bootstrap', 'jquery', 'api', 'rest', 'microservices'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in text_lower:
                # Check if it's a complete word match to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower, re.IGNORECASE):
                    found_skills.append(skill.title())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)
        
        return unique_skills
    
    def preprocess_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline for a resume.
        """
        if not resume_text or not isinstance(resume_text, str):
            return {
                'cleaned_text': '',
                'processed_tokens': [],
                'skills': [],
                'original_text': resume_text
            }
        
        # Clean the text
        cleaned_text = self.clean_text(resume_text)
        
        # Extract skills
        skills = self.extract_skills(resume_text)
        
        # Process tokens
        processed_tokens = self.tokenize_and_process(cleaned_text)
        
        return {
            'cleaned_text': cleaned_text,
            'processed_tokens': processed_tokens,
            'skills': skills,
            'original_text': resume_text
        }


# Global instance
preprocessor = ResumePreprocessor()