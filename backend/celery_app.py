from celery import Celery
from celery.schedules import crontab
from flask import Flask
import os

def create_celery(app):
    # Get Redis URL from environment or use default
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    celery = Celery(
        app.import_name,
        backend=redis_url,
        broker=redis_url
    )
    
    # Optimized Celery configuration
    celery.conf.update(
        # Task routing
        task_routes={
            'backend.tasks.daily_quiz_reminders': {'queue': 'notifications'},
            'backend.tasks.monthly_performance_reports': {'queue': 'reports'},
            'backend.tasks.send_email': {'queue': 'notifications'},
            'backend.tasks.send_gchat_notification': {'queue': 'notifications'},
        },
        
        # Task execution settings
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Kolkata',
        enable_utc=False,
        
        # Worker settings
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
        worker_disable_rate_limits=True,
        
        # Task settings
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        task_always_eager=False,
        
        # Result backend settings
        result_expires=3600,  # 1 hour
        result_backend_transport_options={
            'master_name': 'mymaster',
            'visibility_timeout': 3600,
        },
        
        # Beat schedule for periodic tasks
        beat_schedule={
            'daily-quiz-reminders': {
                'task': 'backend.tasks.daily_quiz_reminders',
                'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
                'options': {'queue': 'notifications'}
            },
            'monthly-performance-reports': {
                'task': 'backend.tasks.monthly_performance_reports',
                'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of month at 9 AM
                'options': {'queue': 'reports'}
            },
        },
        
        # Queue settings
        task_default_queue='default',
        task_default_exchange='default',
        task_default_routing_key='default',
        
        # Monitoring
        worker_send_task_events=True,
        task_send_sent_event=True,
        
        # Error handling
        task_soft_time_limit=300,  # 5 minutes
        task_time_limit=600,       # 10 minutes
        worker_cancel_long_running_tasks_on_connection_loss=True,
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def make_celery():
    app = Flask(__name__)
    app.config.update(
        CELERY_BROKER_URL=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        CELERY_RESULT_BACKEND=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    )
    return create_celery(app)

celery = make_celery() 