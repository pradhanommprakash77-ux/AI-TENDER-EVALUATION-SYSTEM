#!/usr/bin/env python3
"""
AI Tender Evaluation System - Main Launcher
Run this file to start the complete application
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading

def check_dependencies():
    """Check if required packages are installed"""
    print("📦 Checking dependencies...")
    try:
        import flask
        import PyPDF2
        import spacy
        print("✅ All core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required packages"""
    print("📥 Installing dependencies...")
    requirements_path = os.path.join('backend', 'requirements.txt')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])
    print("✅ Dependencies installed")

def download_spacy_model():
    """Download spaCy English model"""
    print("📥 Downloading NLP model (first time only)...")
    subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
    print("✅ NLP model downloaded")

def run_backend():
    """Start the Flask backend server"""
    print("\n🚀 Starting backend server...")
    backend_path = os.path.join('backend', 'app.py')
    os.environ['FLASK_ENV'] = 'development'
    subprocess.call([sys.executable, backend_path])

def open_browser():
    """Open browser after a short delay"""
    time.sleep(3)
    print("\n🌐 Opening application in browser...")
    webbrowser.open('http://localhost:5000')
    webbrowser.open('http://localhost:5000')  # Backend API
    webbrowser.open('file://' + os.path.abspath(os.path.join('frontend', 'index.html')))

def create_sample_data():
    """Create sample PDF files for testing"""
    print("\n📝 Creating sample data for testing...")
    
    # Create data directory
    os.makedirs('data/sample_bids', exist_ok=True)
    
    # Create a simple text file as placeholder
    # In real system, you'd have actual PDFs
    with open('data/sample_tender.txt', 'w') as f:
        f.write("""TENDER DOCUMENT
Project: Construction of 10 Primary Schools in Odisha
Eligibility Criteria:
- Minimum 5 years experience in school construction
- Annual turnover of at least ₹50 Lakhs
- Valid GST, PAN, EPF, ESI certificates required
- Must have completed at least 3 similar projects
""")
    
    print("✅ Sample data created")
    print("   Note: For testing, please upload your own PDF files")
    print("   Sample tender description saved to data/sample_tender.txt")

def main():
    """Main entry point"""
    print("="*60)
    print("🏛️  AI TENDER EVALUATION SYSTEM")
    print("   Government of Odisha - Intelligent Procurement")
    print("="*60)
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('backend/__pycache__', exist_ok=True)
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚙️  Installing dependencies...")
        install_dependencies()
        download_spacy_model()
    
    # Create sample data
    create_sample_data()
    
    print("\n" + "="*60)
    print("✅ System Ready!")
    print("="*60)
    print("\n📋 Instructions:")
    print("1. The backend server will start automatically")
    print("2. Your browser will open with the application")
    print("3. Upload tender document and bid proposals")
    print("4. Click 'Evaluate Bids' to see AI analysis")
    print("\n📁 Project Structure:")
    print("   - backend/    : Python Flask API and AI logic")
    print("   - frontend/   : HTML/CSS/JavaScript interface")
    print("   - uploads/    : Temporary file storage")
    print("   - data/       : Sample data for testing")
    print("\n⚠️  Note: This is a prototype. In production:")
    print("   - Add authentication & security")
    print("   - Connect to government databases")
    print("   - Deploy on State Data Centre")
    print("   - Add more sophisticated AI models")
    print("\n" + "="*60)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Open browser
    open_browser()
    
    print("\n🔄 System running. Press Ctrl+C to stop...")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        print("Thank you for using AI Tender Evaluation System!")
        sys.exit(0)

if __name__ == '__main__':
    main()