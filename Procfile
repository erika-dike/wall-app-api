web: cd wall_app; daphne wall_app.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
worker: cd wall_app; python manage.py runworker -v2
