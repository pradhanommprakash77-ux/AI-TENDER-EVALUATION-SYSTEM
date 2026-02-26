from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor
from evaluation_engine import EvaluationEngine
from risk_analyzer import RiskAnalyzer
import tempfile

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize components
doc_processor = DocumentProcessor()
eval_engine = EvaluationEngine()
risk_analyzer = RiskAnalyzer()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return jsonify({
        'message': 'AI Tender Evaluation System API',
        'status': 'running',
        'endpoints': {
            '/upload': 'POST - Upload tender document',
            '/upload_bids': 'POST - Upload multiple bid documents',
            '/evaluate': 'POST - Evaluate uploaded bids',
            '/results': 'GET - Get evaluation results',
            '/download_report': 'GET - Download evaluation report'
        }
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a single file (tender or bid)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file
        result = doc_processor.process_bid(filepath)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'data': result
        })
        
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/upload_bids', methods=['POST'])
def upload_bids():
    """Upload multiple bid documents"""
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
        
    files = request.files.getlist('files[]')
    results = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the file
            result = doc_processor.process_bid(filepath)
            results.append(result)
            
    return jsonify({
        'message': f'{len(results)} files uploaded successfully',
        'results': results
    })

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """Evaluate all uploaded bids"""
    # Get all PDF files in upload folder
    bid_files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith('.pdf'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            bid_files.append(filepath)
            
    if not bid_files:
        return jsonify({'error': 'No bid documents found'}), 400
        
    # Process all bids
    all_bids_data = []
    for filepath in bid_files:
        bid_data = doc_processor.process_bid(filepath)
        all_bids_data.append(bid_data)
        
    # Evaluate bids
    evaluated_bids = eval_engine.evaluate_all_bids(all_bids_data)
    
    # Analyze risks
    risk_report = risk_analyzer.analyze_all_risks(evaluated_bids)
    
    return jsonify({
        'total_bids': len(evaluated_bids),
        'evaluated_bids': evaluated_bids,
        'risk_report': risk_report,
        'summary': {
            'highly_recommended': sum(1 for b in evaluated_bids if b.get('status') == 'Highly Recommended'),
            'recommended': sum(1 for b in evaluated_bids if b.get('status') == 'Recommended'),
            'not_recommended': sum(1 for b in evaluated_bids if b.get('status') == 'Not Recommended'),
            'non_compliant': sum(1 for b in evaluated_bids if b.get('status') == 'Non-Compliant')
        }
    })

@app.route('/results', methods=['GET'])
def get_results():
    """Get the latest evaluation results"""
    # In a real app, you'd store results in a database
    # For now, we'll just return a message
    return jsonify({
        'message': 'Please run /evaluate first to get results'
    })

@app.route('/download_report', methods=['GET'])
def download_report():
    """Download evaluation report as JSON"""
    # This would generate and send a file
    # For now, just return a placeholder
    return jsonify({
        'message': 'Report generation not implemented in demo'
    })

if __name__ == '__main__':
    print("="*50)
    print("AI TENDER EVALUATION SYSTEM")
    print("="*50)
    print("\nStarting server...")
    print("Access the application at: http://localhost:5000")
    print("\nTo use the system:")
    print("1. Open frontend/index.html in your browser")
    print("2. Upload tender document and bid proposals")
    print("3. Click 'Evaluate Bids' to see results")
    print("="*50)
    
    app.run(debug=True, port=5000)