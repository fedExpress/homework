Quick Setup
-----------

1. Clone this repository.
2. Create a virtualenv and install the requirements.
3. Run redis-server.
4. Start a Celery worker: celery worker -A app.celery --loglevel=info`.
5. Start the Flask application : python app.py.
6. Go to `http://localhost:5000/` !
