from app import create_app
import os # Add this import

app = create_app()

# Add this line for debugging
print(f"--- Loading TMDB Key: {os.environ.get('TMDB_API_KEY')} ---")

if __name__ == '__main__':
    app.run(debug=True) # It's better to run in debug mode for development