# Gunicorn configuration file
import multiprocessing

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Timeout settings
timeout = 120  # Increase timeout to 120 seconds
graceful_timeout = 30

# Worker settings
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'khcc-datahub'

# SSL settings (if needed)
keyfile = None
certfile = None

# Debugging
reload = False
capture_output = True
enable_stdio_inheritance = True 