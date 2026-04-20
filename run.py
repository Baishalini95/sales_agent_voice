import subprocess
import sys
import os

def install_requirements():
    packages = ['flask', 'transformers', 'torch', 'sentence-transformers', 'faiss-cpu', 'PyPDF2', 'flask-cors']
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    print("RAG Chatbot Setup")
    print("=" * 30)
    
    install_requirements()
    
    print("\nStarting server...")
    print("Open http://localhost:5000 in your browser")
    
    subprocess.run([sys.executable, "app.py"])

if __name__ == "__main__":
    main()