# -*- coding: utf-8 -*-

"""
This is the main entry point for the application.
It creates the Flask application instance and starts the server.
"""

from app import create_app
from app.extensions import db

# Create the Flask application instance
app = create_app()

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
