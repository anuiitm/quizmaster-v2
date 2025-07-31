import csv
import os
from datetime import datetime, timedelta, timezone
from backend.celery_app import celery
from backend.models.model import QuizResult, Quiz, Chapter, Subject, User
from backend.extensions import db
from backend.app import create_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Email configuration
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
GCHAT_WEBHOOK_URL = os.environ.get('GCHAT_WEBHOOK_URL', '')

@celery.task(bind=True, name='backend.tasks.test_task')
def test_task(self):
    return {
        'status': 'success',
        'message': 'Test task completed successfully'
    }

@celery.task
def send_email(to_email, subject, body, html_body=None):
    """Send email using SMTP"""
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            return {
                'status': 'error',
                'message': 'Email configuration not set'
            }
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        
        # Attach text and HTML parts
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return {
            'status': 'success',
            'message': f'Email sent to {to_email}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

@celery.task
def send_gchat_notification(message):
    """Send notification to Google Chat"""
    try:
        if not GCHAT_WEBHOOK_URL:
            return {
                'status': 'error',
                'message': 'Google Chat webhook URL not configured'
            }
        
        payload = {
            'text': message
        }
        
        response = requests.post(GCHAT_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        
        return {
            'status': 'success',
            'message': 'Google Chat notification sent'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

@celery.task
def daily_quiz_reminders():
    """Send daily quiz reminders to users"""
    try:
        app = create_app()
        with app.app_context():
            # Get all users who haven't taken a quiz in the last 7 days
            seven_days_ago = datetime.now(IST) - timedelta(days=7)
            
            users = User.query.filter(
                ~User.id.in_(
                    db.session.query(QuizResult.user_id).filter(
                        QuizResult.date_taken >= seven_days_ago
                    )
                )
            ).all()
            
            if not users:
                return {
                    'status': 'success',
                    'message': 'No users need reminders'
                }
            
            # Send reminders
            sent_count = 0
            for user in users:
                try:
                    # Send email reminder
                    subject = "Quiz Reminder - Don't forget to practice!"
                    body = f"""
                    Hi {user.full_name},
                    
                    It's been a while since you last took a quiz. Don't forget to practice and improve your skills!
                    
                    Login to your account and take some quizzes to stay sharp.
                    
                    Best regards,
                    QuizMaster Team
                    """
                    
                    email_task = send_email.delay(
                        user.email,
                        subject,
                        body
                    )
                    
                    # Send Google Chat notification if configured
                    if GCHAT_WEBHOOK_URL:
                        gchat_task = send_gchat_notification.delay(
                            f"📚 Quiz Reminder sent to {user.full_name} ({user.email})"
                        )
                    
                    sent_count += 1
                    
                except Exception as e:
                    continue
            
            return {
                'status': 'success',
                'message': f'Reminders sent to {sent_count} users'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

@celery.task
def monthly_performance_reports():
    """Generate and send monthly performance reports"""
    try:
        app = create_app()
        with app.app_context():
            # Get all users
            users = User.query.all()
            
            if not users:
                return {
                    'status': 'success',
                    'message': 'No users to generate reports for'
                }
            
            # Generate reports for each user
            reports_sent = 0
            for user in users:
                try:
                    # Get user's quiz results for the last month
                    one_month_ago = datetime.now(IST) - timedelta(days=30)
                    results = QuizResult.query.filter(
                        QuizResult.user_id == user.id,
                        QuizResult.date_taken >= one_month_ago
                    ).all()
                    
                    if not results:
                        continue
                    
                    # Calculate statistics
                    total_quizzes = len(results)
                    total_score = sum(r.score for r in results)
                    average_score = total_score / total_quizzes
                    highest_score = max(r.score for r in results)
                    lowest_score = min(r.score for r in results)
                    
                    # Generate report
                    subject = "Your Monthly Quiz Performance Report"
                    body = f"""
                    Hi {user.full_name},
                    
                    Here's your monthly quiz performance report:
                    
                    📊 Monthly Statistics:
                    - Total Quizzes Taken: {total_quizzes}
                    - Average Score: {average_score:.1f}%
                    - Highest Score: {highest_score}%
                    - Lowest Score: {lowest_score}%
                    
                    Keep up the great work and continue practicing!
                    
                    Best regards,
                    QuizMaster Team
                    """
                    
                    # Send report
                    email_task = send_email.delay(
                        user.email,
                        subject,
                        body
                    )
                    
                    reports_sent += 1
                    
                except Exception as e:
                    continue
            
            return {
                'status': 'success',
                'message': f'Monthly reports sent to {reports_sent} users'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        } 