# AI-Powered Resume Analyzer & Job Role Classifier

A production-grade system for analyzing resumes and classifying them into appropriate job roles using machine learning.

## Features

- **ML-Powered Classification**: Uses your trained model for job role prediction
- **Deep Resume Analysis**: Extracts skills, experience level, and provides insights
- **MongoDB Integration**: Stores analysis results and maintains history
- **RESTful API**: Cloud-ready Flask backend with comprehensive endpoints
- **Mobile-Ready**: Designed for integration with Flutter mobile app

## Architecture

```
project_root/
├── models/                    # ML models (model.pkl, vectorizer.pkl, label_encoder.pkl)
├── data/                      # Dataset (resume_clean_preprocessed.csv)
├── app/                       # Core application modules
│   ├── model_loader.py        # Singleton model loader
│   ├── preprocessing.py       # Text preprocessing pipeline
│   ├── inference.py           # ML inference engine
│   ├── mongo_service.py       # MongoDB operations
│   └── utils.py               # Utility functions
├── api/                       # API routes (handled in app.py)
├── mobile/                    # Flutter mobile application
├── logs/                      # Application logs
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── Procfile                   # Deployment configuration
├── .env                       # Environment variables
└── README.md
```

## API Endpoints

- `POST /predict` - Classify resume and return job category with confidence
- `POST /analyze` - Deep resume analysis with comprehensive insights
- `POST /store-result` - Store analysis results manually
- `GET /history` - Retrieve previous analysis history
- `GET /health` - Health check endpoint
- `GET /version` - Version information

## Response Format

```json
{
  "success": true,
  "data": {
    "job_category": "Software Engineering",
    "confidence": 0.85,
    "skills": ["Python", "JavaScript", "React"],
    "experience_level": "Mid-Level",
    "summary": "This resume aligns with Software Engineering role...",
    "timestamp": "2023-12-30T16:44:00Z",
    "resume_id": "resume_20231230_1644_abcdef12"
  },
  "timestamp": "2023-12-30T16:44:00Z"
}
```

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd resume-analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URI
   ```

4. **Ensure model files are in place**
   ```
   models/
   ├── model.pkl
   ├── vectorizer.pkl
   └── label_encoder.pkl
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## Cloud Deployment

The application is ready for deployment on platforms like Render, Railway, or Deta:

- Uses Gunicorn as WSGI server
- Binds to PORT environment variable
- Loads models once at startup
- Statelessness ensured for horizontal scaling

## Environment Variables

- `MONGO_URI`: MongoDB connection string (defaults to local)
- `DB_NAME`: Database name (defaults to `resume_ai_db`)
- `PORT`: Port to bind to (defaults to 5000)

## Data Storage

Results are stored in MongoDB with the following collections:
- `resume_analysis_logs`: Stores all analysis results
- `users`: User information (if applicable)
- `feedback`: User feedback on predictions

## Model Integration

The system uses a singleton pattern to load models once at startup, ensuring:
- Thread-safe inference
- Fast response times
- Efficient memory usage

## Flutter Mobile App

The backend is designed to integrate seamlessly with a Flutter mobile application that provides:
- Resume text input
- Job category display
- Confidence scores
- Skill extraction
- Analysis history