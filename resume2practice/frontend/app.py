from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import uuid
import os
from werkzeug.utils import secure_filename
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:5000')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage for large data (use Redis in production)
session_storage = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_thread_id():
    """Generate a unique thread ID for the session"""
    return str(uuid.uuid4())

def store_session_data(session_id, key, data):
    """Store large data outside of Flask session"""
    if session_id not in session_storage:
        session_storage[session_id] = {}
    session_storage[session_id][key] = data

def get_session_data(session_id, key, default=None):
    """Retrieve data from session storage"""
    return session_storage.get(session_id, {}).get(key, default)

@app.route('/')
def index():
    """Main page for resume and job description input"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle the initial analysis request"""
    try:
        # Generate thread ID and session ID for this session
        thread_id = generate_thread_id()
        session_id = str(uuid.uuid4())
        
        session['thread_id'] = thread_id
        session['session_id'] = session_id
        
        # Prepare form data for backend
        form_data = {
            'thread_id': thread_id
        }
        files = {}
        
        # Handle resume input
        if 'resume_text' in request.form and request.form['resume_text'].strip():
            form_data['resume_text'] = request.form['resume_text']
        elif 'resume_file' in request.files:
            resume_file = request.files['resume_file']
            if resume_file and resume_file.filename and allowed_file(resume_file.filename):
                files['resume_file'] = (resume_file.filename, resume_file.read(), resume_file.content_type)
            else:
                return jsonify({'error': 'Invalid resume file. Only PDF files are allowed.'}), 400
        else:
            return jsonify({'error': 'Please provide a resume either as text or PDF file.'}), 400
        
        # Handle job description input
        if 'job_description_text' in request.form and request.form['job_description_text'].strip():
            form_data['job_description_text'] = request.form['job_description_text']
        elif 'job_description_file' in request.files:
            jd_file = request.files['job_description_file']
            if jd_file and jd_file.filename and allowed_file(jd_file.filename):
                files['job_description_file'] = (jd_file.filename, jd_file.read(), jd_file.content_type)
            else:
                return jsonify({'error': 'Invalid job description file. Only PDF files are allowed.'}), 400
        else:
            return jsonify({'error': 'Please provide a job description either as text or PDF file.'}), 400
        
        # Make request to backend
        backend_url = f"{BACKEND_URL}/analyze"
        logger.info(f"Making request to backend: {backend_url}")
        logger.info(f"Form data keys: {list(form_data.keys())}")
        logger.info(f"Files: {list(files.keys()) if files else 'None'}")
        
        try:
            if files:
                response = requests.post(backend_url, data=form_data, files=files, timeout=120)
            else:
                response = requests.post(backend_url, data=form_data, timeout=120)
            
            logger.info(f"Backend response status: {response.status_code}")
            logger.info(f"Backend response headers: {dict(response.headers)}")
            logger.info(f"Backend response content (first 500 chars): {response.text[:500]}")
            
        except requests.exceptions.RequestException as req_error:
            logger.error(f"Request error: {str(req_error)}")
            return jsonify({'error': f'Failed to connect to backend: {str(req_error)}'}), 500
        
        if response.status_code == 200:
            try:
                questions_data = response.json()
                
                # Handle case where backend returns a string instead of dict
                if isinstance(questions_data, str):
                    try:
                        questions_data = json.loads(questions_data)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse backend response as JSON: {questions_data}")
                        return jsonify({'error': 'Invalid response format from backend'}), 500
                
                # Store questions data in external storage instead of session
                store_session_data(session_id, 'questions_data', questions_data)
                
                # Extract questions from the response
                questions = []
                if isinstance(questions_data, dict):
                    questions = questions_data.get('questions', [])
                elif isinstance(questions_data, list):
                    questions = questions_data
                
                return jsonify({
                    'success': True,
                    'questions': questions,
                    'thread_id': thread_id
                })
                
            except Exception as json_error:
                logger.error(f"Error parsing backend response: {str(json_error)}")
                logger.error(f"Raw response content: {response.text}")
                return jsonify({'error': f'Failed to parse backend response: {str(json_error)}'}), 500
        else:
            logger.error(f"Backend error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Backend error: {response.text}'}), response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({'error': f'Failed to connect to backend: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    """Handle the submission of answers to questions"""
    try:
        data = request.get_json()
        thread_id = session.get('thread_id')
        session_id = session.get('session_id')
        
        if not thread_id or not session_id:
            return jsonify({'error': 'No active session found. Please start over.'}), 400
        
        # Format questions and answers
        questions_data = get_session_data(session_id, 'questions_data', {})
        questions = questions_data.get('questions', [])
        answers = data.get('answers', [])
        
        # Create formatted response text
        response_text = ""
        for i, question in enumerate(questions):
            answer = answers[i] if i < len(answers) else ""
            if answer.strip():  # Only include answered questions
                response_text += f"Q: {question}\nA: {answer}\n\n"
        
        if not response_text.strip():
            response_text = "No additional information provided."
        
        # Send to backend resume endpoint
        backend_url = f"{BACKEND_URL}/resume"
        payload = {
            'thread_id': thread_id,
            'response': response_text
        }
        
        logger.info(f"Submitting answers to backend: {backend_url}")
        logger.info(f"Payload: {payload}")
        response = requests.post(backend_url, json=payload, timeout=120)
        
        logger.info(f"Resume backend response status: {response.status_code}")
        logger.info(f"Resume backend response headers: {dict(response.headers)}")
        logger.info(f"Resume backend response content: {response.text}")
        
        if response.status_code == 200:
            result_data = response.json()
            logger.info(f"Parsed result_data type: {type(result_data)}")
            logger.info(f"Parsed result_data keys: {list(result_data.keys()) if isinstance(result_data, dict) else 'Not a dict'}")
            
            # Check if this is still returning questions instead of final results
            if isinstance(result_data, dict) and 'questions' in result_data:
                logger.error("Backend returned questions again instead of final results!")
                logger.error(f"Questions returned: {result_data.get('questions', [])}")
                return jsonify({'error': 'Backend workflow did not complete properly. Still returning questions.'}), 500
            
            # Store result data in external storage
            store_session_data(session_id, 'result_data', result_data)
            return jsonify({
                'success': True,
                'redirect': '/results'
            })
        else:
            logger.error(f"Backend error: {response.status_code} - {response.text}")
            return jsonify({'error': f'Backend error: {response.text}'}), response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({'error': f'Failed to connect to backend: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/results')
def results():
    """Display the final results (scorecard and tasks)"""
    session_id = session.get('session_id')
    if not session_id:
        return render_template('error.html', error="No active session found. Please start over.")
    
    result_data = get_session_data(session_id, 'result_data')
    if not result_data:
        return render_template('error.html', error="No results found. Please start over.")
    
    # Debug logging
    logger.info(f"Result data type: {type(result_data)}")
    logger.info(f"Result data keys: {list(result_data.keys()) if isinstance(result_data, dict) else 'Not a dict'}")
    
    # Handle case where result_data might be a string (JSON)
    if isinstance(result_data, str):
        try:
            result_data = json.loads(result_data)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse result_data as JSON: {result_data}")
            return render_template('error.html', error="Invalid result data format.")
    
    # Extract scorecard and task_list with safe defaults
    scorecard_raw = result_data.get('scorecard', {})
    task_list_raw = result_data.get('task_list', {})
    
    # Debug logging for scorecard
    logger.info(f"Scorecard raw type: {type(scorecard_raw)}")
    logger.info(f"Scorecard raw content: {scorecard_raw}")
    
    # Handle scorecard - might be a string (JSON) or dict
    scorecard = {}
    if isinstance(scorecard_raw, str):
        try:
            scorecard = json.loads(scorecard_raw)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse scorecard as JSON: {scorecard_raw}")
            scorecard = {}
    elif isinstance(scorecard_raw, dict):
        scorecard = scorecard_raw
    else:
        logger.error(f"Unexpected scorecard type: {type(scorecard_raw)}")
        scorecard = {}
    
    # Handle task_list - might be a string (JSON) or dict
    task_list = {}
    if isinstance(task_list_raw, str):
        try:
            task_list = json.loads(task_list_raw)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse task_list as JSON: {task_list_raw}")
            task_list = {}
    elif isinstance(task_list_raw, dict):
        task_list = task_list_raw
    else:
        logger.error(f"Unexpected task_list type: {type(task_list_raw)}")
        task_list = {}
    
    # Ensure scorecard has required fields with defaults
    if not scorecard or not isinstance(scorecard, dict):
        scorecard = {
            'gap_analysis': 'No gap analysis available',
            'strengths': [],
            'weaknesses': [],
            'opportunity_for_growth': 'No growth opportunities identified',
            'readiness_score': 0.0
        }
    else:
        # Ensure all required fields exist
        scorecard.setdefault('gap_analysis', 'No gap analysis available')
        scorecard.setdefault('strengths', [])
        scorecard.setdefault('weaknesses', [])
        scorecard.setdefault('opportunity_for_growth', 'No growth opportunities identified')
        scorecard.setdefault('readiness_score', 0.0)
    
    # Ensure task_list has required structure
    if not task_list or not isinstance(task_list, dict) or 'tasks' not in task_list:
        task_list = {'tasks': []}
    
    # Ensure readiness_score is a number
    try:
        scorecard['readiness_score'] = float(scorecard['readiness_score'])
    except (ValueError, TypeError):
        scorecard['readiness_score'] = 0.0
    
    # Debug logging final data
    logger.info(f"Final scorecard: {scorecard}")
    logger.info(f"Final task_list: {task_list}")
    
    return render_template('results.html', 
                         scorecard=scorecard,
                         task_list=task_list)

@app.route('/debug_last_response')
def debug_last_response():
    """Debug route to see the last backend response"""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No session_id found'})
    
    result_data = get_session_data(session_id, 'result_data')
    questions_data = get_session_data(session_id, 'questions_data')
    
    return jsonify({
        'session_id': session_id,
        'thread_id': session.get('thread_id'),
        'result_data_type': str(type(result_data)),
        'result_data': result_data,
        'questions_data_type': str(type(questions_data)),
        'questions_data': questions_data,
        'session_storage_keys': list(session_storage.get(session_id, {}).keys()) if session_id in session_storage else []
    })

@app.route('/debug_session')
def debug_session():
    """Debug route to see what's in the session storage"""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No session_id found'})
    
    result_data = get_session_data(session_id, 'result_data')
    return jsonify({
        'session_id': session_id,
        'result_data_type': str(type(result_data)),
        'result_data': result_data,
        'session_storage_keys': list(session_storage.get(session_id, {}).keys())
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')