"""Production server configuration with Gunicorn-like settings.

For true production, use: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
"""
import multiprocessing

# Calculate optimal workers
workers = multiprocessing.cpu_count() * 2 + 1

print(f"""
Production Configuration Recommendations:
==========================================

1. Install Gunicorn:
   pip install gunicorn

2. Run with multiple workers:
   gunicorn app.main:app \\
     --workers {workers} \\
     --worker-class uvicorn.workers.UvicornWorker \\
     --bind 0.0.0.0:8000 \\
     --timeout 120 \\
     --keep-alive 5 \\
     --max-requests 1000 \\
     --max-requests-jitter 50

3. For development with better performance:
   uvicorn app.main:app \\
     --host 0.0.0.0 \\
     --port 8000 \\
     --workers {workers} \\
     --timeout-keep-alive 5

Current System:
- CPU Cores: {multiprocessing.cpu_count()}
- Recommended Workers: {workers}
- Each worker can handle ~25-30 concurrent requests
- Total capacity: ~{workers * 25}-{workers * 30} concurrent users

Note: Multiple workers require more database connections.
Adjust database pool_size accordingly.
""")
