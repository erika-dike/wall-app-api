web: gunicorn wall_app.asgi --pythonpath=wall_app --timeout 15 --keep-alive 5 --log-level debug --log-file -
worker: python manage.py runworker
