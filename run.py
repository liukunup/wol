# -*- coding: utf-8 -*-

"""
This is the main entry point for the application.
It creates the Flask application instance and starts the server.
"""

from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000)
