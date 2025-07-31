#!/usr/bin/env python3
"""
Celery worker script for running background tasks
"""
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.celery_app import celery
# Import tasks to register them with Celery
import backend.tasks

if __name__ == '__main__':
    # Start the Celery worker
    celery.worker_main(['worker', '--loglevel=info']) 