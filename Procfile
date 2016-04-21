web: gunicorn "jaypeak:create_app()"
worker: celery worker -A lifts.main.tasks -l info