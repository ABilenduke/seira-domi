import os
from app import create_app, celery

environment = os.getenv("FLASK_ENV") or "production"
is_debug = environment != "production"

if __name__ == "__main__":
    app = create_app(celery=celery)
    app.run(debug=is_debug)
