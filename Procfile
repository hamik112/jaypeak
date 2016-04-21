web: gunicorn "jaypeak:create_app()"
worker: celery worker -A jaypeak.transactions.tasks -l info