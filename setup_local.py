import os
import shutil
import subprocess
import sys

def setup():
    print("====================================================")
    print("          Atmosphere-AI Local Setup Script          ")
    print("====================================================")
    
    # 1. Copy .env.example to .env if it doesn't exist
    if not os.path.exists(".env"):
        print("Creating '.env' configuration file from '.env.example'...")
        shutil.copy(".env.example", ".env")
        print("'.env' file created successfully.")
    else:
        print("'.env' configuration file already exists. Skipping creation.")
        
    # 2. Check and install dependencies
    print("Installing Python package dependencies from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        print("Please run 'pip install -r requirements.txt' manually.")
        
    # 3. Initialize local database
    print("Initializing and seeding local database...")
    try:
        import database
        database.init_db()
        print("Database initialized and seeded successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        
    print("\nSetup complete! To run the application locally:")
    print("1. Start the Flask server:")
    print("   python app.py")
    print("2. Open your browser and navigate to:")
    print("   http://127.0.0.1:5000/")
    print("====================================================")

if __name__ == "__main__":
    setup()
