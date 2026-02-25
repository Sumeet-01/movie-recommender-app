"""
CineMate - Movie Recommendation Platform
Single command startup: python run.py
"""

import os
import sys
import shutil
import warnings

# Suppress all deprecation/resource warnings for clean console output
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=ResourceWarning)
warnings.filterwarnings('ignore', message='.*urllib3.*')
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'


def clear_pycache(root):
    """Remove __pycache__ dirs to prevent stale bytecode hangs on Windows."""
    for dirpath, dirnames, _ in os.walk(root):
        for d in dirnames:
            if d == '__pycache__':
                shutil.rmtree(os.path.join(dirpath, d), ignore_errors=True)


def main():
    """Initialize and run CineMate application."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Clean stale bytecode (prevents Windows import hangs)
    clear_pycache(os.path.join(base_dir, 'app'))

    # Banner
    print()
    print("=" * 60)
    print("    CineMate - Your Intelligent Movie Companion")
    print("    Netflix-style Movie Discovery & Recommendations")
    print("=" * 60)
    print()

    # Check .env
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print("  ERROR: .env file not found!")
        print("  Copy .env.example to .env and add your TMDB API key.")
        sys.exit(1)

    # Load env
    from dotenv import load_dotenv
    load_dotenv(env_path)

    if not os.environ.get('TMDB_API_KEY'):
        print("  ERROR: TMDB_API_KEY not set in .env")
        print("  Get a free key: https://www.themoviedb.org/settings/api")
        sys.exit(1)

    print("  Environment loaded")
    print(f"  Database: {os.environ.get('DATABASE_URL', 'sqlite:///cinemate.db')}")
    print(f"  TMDB API: {'Bearer Token' if os.environ.get('TMDB_API_KEY', '').startswith('eyJ') else 'API Key'}")
    print()

    # Create app
    from app import create_app
    app = create_app()

    # Print startup info
    host = '127.0.0.1'
    port = int(os.environ.get('PORT', 5000))
    
    print()
    print("-" * 60)
    print(f"    Server running at: http://{host}:{port}")
    print(f"    Press Ctrl+C to stop")
    print("-" * 60)
    print()

    app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    main()
