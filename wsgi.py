import os

from app import create_app

environment = os.getenv("FLASK_ENV") or "production"

app = create_app(environment)

if __name__ == "__main__":
    is_debug = environment != "production"
    app.run(debug=is_debug)