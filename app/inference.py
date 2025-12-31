import numpy as np
import logging
from typing import Dict, List, Any, Tuple
from .model_loader import model_loader
from .preprocessing import preprocessor

logger = logging.getLogger(__name__)

class ResumeInference:
    """
    Handles inference operations for resume classification.
    """
    
    def __init__(self):
        self.model = model_loader.get_model()
        self.vectorizer = model_loader.get_vectorizer()
        self.label_encoder = model_loader.get_label_encoder()
        
        if not all([self.model, self.vectorizer, self.label_encoder]):
            raise RuntimeError("Failed to load all required models for inference")
    
    def predict_job_category(self, resume_text: str) -> Dict[str, Any]:
        """
        Predict job category for a given resume text.
        Returns a dictionary with prediction results.
        """
        try:
            # Preprocess the resume text
            processed_data = preprocessor.preprocess_resume(resume_text)
            cleaned_text = processed_data['cleaned_text']
            
            # Vectorize the text
            text_vector = self.vectorizer.transform([cleaned_text])
            
            # Make prediction
            prediction = self.model.predict(text_vector)
            prediction_proba = self.model.predict_proba(text_vector)
            
            # Get the predicted class
            predicted_label = self.label_encoder.inverse_transform(prediction)[0]
            
            # Get confidence score (max probability)
            confidence = float(np.max(prediction_proba))
            
            # Get experience level based on resume content (simplified approach)
            experience_level = self._infer_experience_level(resume_text)
            
            # Generate summary
            summary = self._generate_summary(predicted_label, confidence, processed_data['skills'])
            
            result = {
                'job_category': predicted_label,
                'confidence': round(confidence, 2),
                'skills': processed_data['skills'],
                'experience_level': experience_level,
                'summary': summary,
                'timestamp': self._get_current_timestamp()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error during inference: {e}")
            raise
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Perform deep analysis of the resume beyond just classification.
        """
        try:
            # Preprocess the resume
            processed_data = preprocessor.preprocess_resume(resume_text)
            
            # Perform prediction
            prediction_result = self.predict_job_category(resume_text)
            
            # Additional analysis
            word_count = len(resume_text.split())
            char_count = len(resume_text)
            avg_sentence_length = self._calculate_avg_sentence_length(resume_text)
            
            # Extract key sections (simplified approach)
            sections = self._extract_resume_sections(resume_text)
            
            analysis = {
                **prediction_result,  # Include prediction results
                'word_count': word_count,
                'character_count': char_count,
                'avg_sentence_length': avg_sentence_length,
                'sections': sections,
                'keywords': processed_data['processed_tokens'][:20],  # Top 20 keywords
                'readability_score': self._calculate_readability_score(resume_text)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error during resume analysis: {e}")
            raise
    
    def _infer_experience_level(self, resume_text: str) -> str:
        """
        Infer experience level based on keywords in resume.
        """
        resume_lower = resume_text.lower()
        
        # Keywords for different experience levels
        junior_keywords = ['junior', 'entry level', 'intern', 'fresh', 'beginner', 'student', 'graduate']
        mid_keywords = ['mid', 'associate', 'experienced', 'intermediate', '2-5 years', '3-5 years']
        senior_keywords = ['senior', 'lead', 'principal', 'architect', 'manager', 'lead', 'expert', '10+ years']
        
        # Count occurrences
        junior_count = sum(1 for keyword in junior_keywords if keyword in resume_lower)
        mid_count = sum(1 for keyword in mid_keywords if keyword in resume_lower)
        senior_count = sum(1 for keyword in senior_keywords if keyword in resume_lower)
        
        # Determine experience level
        if senior_count > mid_count and senior_count > junior_count:
            return "Senior"
        elif mid_count > junior_count:
            return "Mid-Level"
        elif junior_count > 0:
            return "Junior"
        else:
            # Default based on years of experience mentioned
            import re
            years_match = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', resume_lower)
            if years_match:
                max_years = max([int(y) for y in years_match])
                if max_years >= 8:
                    return "Senior"
                elif max_years >= 3:
                    return "Mid-Level"
                else:
                    return "Junior"
            else:
                return "Mid-Level"  # Default assumption
    
    def _generate_summary(self, job_category: str, confidence: float, skills: List[str]) -> str:
        """
        Generate a summary of the analysis.
        """
        if confidence >= 0.8:
            confidence_desc = "high confidence"
        elif confidence >= 0.6:
            confidence_desc = "moderate confidence"
        else:
            confidence_desc = "low confidence"
        
        skill_str = ", ".join(skills[:5])  # Show top 5 skills
        if len(skills) > 5:
            skill_str += f", and {len(skills) - 5} more"
        
        summary = (f"This resume appears to align with the {job_category} role with {confidence_desc}. "
                  f"Key skills identified: {skill_str}.")
        
        return summary
    
    def _calculate_avg_sentence_length(self, text: str) -> float:
        """
        Calculate average sentence length in words.
        """
        import re
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0
        
        total_words = sum(len(s.split()) for s in sentences)
        avg_length = total_words / len(sentences) if sentences else 0
        
        return round(avg_length, 2)
    
    def _extract_resume_sections(self, text: str) -> List[str]:
        """
        Extract potential sections from the resume (simplified approach).
        """
        import re
        # Common resume section headers
        section_headers = [
            'education', 'experience', 'skills', 'projects', 
            'certifications', 'awards', 'contact', 'summary',
            'objective', 'work experience', 'professional experience'
        ]
        
        found_sections = []
        text_lower = text.lower()
        
        for header in section_headers:
            if header in text_lower:
                found_sections.append(header.title())
        
        return list(set(found_sections))  # Remove duplicates
    
    def _calculate_readability_score(self, text: str) -> float:
        """
        Calculate a simple readability score.
        """
        import re
        
        # Count words
        words = len(text.split())
        
        # Count sentences
        sentences = len(re.split(r'[.!?]+', text))
        
        # Count syllables (simple estimation)
        vowels = "aeiouAEIOU"
        syllable_count = 0
        for char in text:
            if char in vowels:
                syllable_count += 1
        
        # Adjust for silent 'e' at the end of words
        syllable_count -= len(re.findall(r'e\s', text))
        
        if words == 0 or sentences == 0:
            return 0.0
        
        # Calculate Automated Readability Index (simplified)
        # ARI = 4.71 * (characters/words) + 0.5 * (words/sentences) - 21.43
        characters = len(text.replace(' ', ''))
        ari = 4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43
        
        # Return readability score between 0-10
        score = max(0, min(10, 10 - (ari / 2)))  # Adjusted scale
        return round(score, 2)
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


# Global instance
inference_engine = ResumeInference()