#!/usr/bin/env python3
"""
Quick setup script for CineMate development environment.
Run this after cloning the repository to get started quickly.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"   Output: {e.output}")
        return False


def check_python_version():
    """Ensure Python 3.8+ is being used."""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have Python {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")


def create_virtualenv():
    """Create and activate virtual environment."""
    print_header("Setting Up Virtual Environment")
    
    if not os.path.exists('venv'):
        if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
            return False
    else:
        print("ℹ️  Virtual environment already exists")
    
    # Determine activation script based on OS
    if sys.platform == 'win32':
        activate_script = 'venv\\Scripts\\activate'
        print(f"\n💡 To activate the virtual environment, run:")
        print(f"   {activate_script}")
    else:
        activate_script = 'source venv/bin/activate'
        print(f"\n💡 To activate the virtual environment, run:")
        print(f"   {activate_script}")
    
    return True


def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Dependencies")
    
    # Determine pip path
    if sys.platform == 'win32':
        pip_path = 'venv\\Scripts\\pip'
    else:
        pip_path = 'venv/bin/pip'
    
    if not os.path.exists(pip_path):
        print("⚠️  Please activate the virtual environment first and run:")
        print("   pip install -r requirements.txt")
        return True
    
    return run_command(
        f"{pip_path} install -r requirements.txt",
        "Installing Python packages"
    )


def setup_env_file():
    """Create .env file from template."""
    print_header("Setting Up Environment Variables")
    
    if os.path.exists('.env'):
        print("ℹ️  .env file already exists")
        overwrite = input("   Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            return True
    
    if os.path.exists('.env.example'):
        try:
            with open('.env.example', 'r') as src:
                content = src.read()
            with open('.env', 'w') as dst:
                dst.write(content)
            print("✅ Created .env file from template")
            print("\n⚠️  IMPORTANT: Edit .env and add your TMDB_API_KEY")
            print("   Get your key from: https://www.themoviedb.org/settings/api\n")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ .env.example not found")
        return False


def initialize_database():
    """Initialize database with migrations."""
    print_header("Initializing Database")
    
    # Check if migrations folder exists
    if not os.path.exists('migrations'):
        print("📝 Initializing Flask-Migrate...")
        if not run_command("flask db init", "Initialize migrations"):
            return False
    else:
        print("ℹ️  Migrations folder already exists")
    
    # Create migration
    if run_command(
        'flask db migrate -m "Initial migration with all models"',
        "Creating migration"
    ):
        # Apply migration
        return run_command("flask db upgrade", "Applying migration to database")
    
    return False


def seed_database():
    """Ask user if they want to seed the database."""
    print_header("Database Seeding")
    
    seed = input("Would you like to seed the database with sample data? (y/n): ").lower()
    if seed == 'y':
        return run_command(
            f"{sys.executable} scripts/seed_database.py",
            "Seeding database"
        )
    else:
        print("ℹ️  Skipping database seeding")
        return True


def create_instance_folder():
    """Ensure instance folder exists."""
    instance_dir = Path('instance')
    if not instance_dir.exists():
        instance_dir.mkdir()
        print("✅ Created instance directory")
    return True


def main():
    """Run all setup steps."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              🎬  CineMate Setup Script  🎬               ║
    ║                                                           ║
    ║          Advanced Movie Recommendation Platform          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Run setup steps
        check_python_version()
        
        if not create_virtualenv():
            print("\n❌ Setup failed at virtual environment creation")
            sys.exit(1)
        
        print("\n💡 Please activate the virtual environment and run this script again:")
        if sys.platform == 'win32':
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print(f"   {sys.executable} scripts/setup.py\n")
        
        # Note: The following steps require activated venv
        # They will be executed when user runs the script again
        
        # if not install_dependencies():
        #     print("\n❌ Setup failed at dependency installation")
        #     sys.exit(1)
        
        # if not create_instance_folder():
        #     print("\n❌ Setup failed at instance folder creation")
        #     sys.exit(1)
        
        # if not setup_env_file():
        #     print("\n❌ Setup failed at environment setup")
        #     sys.exit(1)
        
        # if not initialize_database():
        #     print("\n❌ Setup failed at database initialization")
        #     sys.exit(1)
        
        # if not seed_database():
        #     print("\n⚠️  Database seeding failed, but setup can continue")
        
        print_header("Setup Instructions")
        print("""
        ✅ Initial setup complete!
        
        📋 Next steps:
        
        1. Activate the virtual environment:
           Windows: venv\\Scripts\\activate
           Linux/Mac: source venv/bin/activate
        
        2. Install dependencies:
           pip install -r requirements.txt
        
        3. Configure environment:
           - Edit .env file
           - Add your TMDB_API_KEY (from https://www.themoviedb.org/settings/api)
        
        4. Initialize database:
           flask db init
           flask db migrate -m "Initial migration"
           flask db upgrade
        
        5. (Optional) Seed database:
           python scripts/seed_database.py
        
        6. Run the application:
           python run.py
           or
           flask run
        
        7. Open in browser:
           http://localhost:5000
        
        📚 For more information, see README.md
        """)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
