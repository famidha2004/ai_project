# gunicorn_config.py
# Configuration for Gunicorn WSGI server in production

workers = 4
worker_class = "sync"
bind = "0.0.0.0:5000"
timeout = 30
keepalive = 2
accesslog = "-"
errorlog = "-"
loglevel = "info"
