from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from backend.models.model import Subject, Chapter, Quiz, Question, User, QuizResult
from backend.extensions import db
from backend.utils.decorators import admin_secure_endpoint
import os
from datetime import datetime, timezone, timedelta

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=100)
def admin_dashboard():
    return jsonify({'message': 'Welcome Admin 👑'}), 200


@admin_bp.route('/create_subject', methods=['POST'])
@admin_secure_endpoint(rate_limit_requests=30)
def create_subject():
    data = request.json or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    errors = {}
    if not name:
        errors['name'] = 'Name is required.'
    if not description:
        errors['description'] = 'Description is required.'

    # Check for duplicate subject name
    existing_subject = Subject.query.filter_by(name=name).first()
    if existing_subject:
        errors['name'] = f'A subject with the name "{name}" already exists.'

    if errors:
        return jsonify({'errors': errors}), 400

    new_subject = Subject(name=name, description=description)
    db.session.add(new_subject)
    db.session.commit()

    return jsonify({'message': 'Subject created successfully'}), 201

@admin_bp.route('/subjects', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def get_subjects():
    try:
        subjects = Subject.query.order_by(Subject.name).all()
        subjects_list = [
            {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description,
                'chapters': [
                    {
                        'id': chapter.id,
                        'name': chapter.name,
                        'description': chapter.description,
                        'question_count': sum([quiz.question_count for quiz in chapter.quizzes])
                    }
                    for chapter in subject.chapters
                ]
            }
            for subject in subjects
        ]
        return jsonify({'subjects': subjects_list}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching subjects.'}), 500


@admin_bp.route('/subject/<int:subject_id>', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    })

@admin_bp.route('/subject/<int:subject_id>', methods=['PUT'])
@admin_secure_endpoint(rate_limit_requests=30)
def update_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    data = request.json or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    errors = {}
    if not name:
        errors['name'] = 'Name is required.'
    if not description:
        errors['description'] = 'Description is required.'
    if errors:
        return jsonify({'errors': errors}), 400
    subject.name = name
    subject.description = description
    db.session.commit()
    
    return jsonify({'message': 'Subject updated successfully'})


@admin_bp.route('/subject/<int:subject_id>', methods=['DELETE'])
@admin_secure_endpoint(rate_limit_requests=20)
def delete_subject(subject_id):
    
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({'message': f'Subject with ID {subject_id} not found'}), 404

    try:
        db.session.delete(subject)
        db.session.commit()
        
        return jsonify({'message': 'Subject deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete subject', 'error': str(e)}), 500


@admin_bp.route('/subject/<int:subject_id>/chapters', methods=['POST'])
@admin_secure_endpoint(rate_limit_requests=30)
def create_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    data = request.json or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    
    errors = {}
    if not name:
        errors['name'] = 'Name is required.'
    if not description:
        errors['description'] = 'Description is required.'
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
    db.session.add(new_chapter)
    db.session.commit()
    
    return jsonify({'message': 'Chapter created successfully'}), 201

@admin_bp.route('/chapter/<int:chapter_id>', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def get_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return jsonify({
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description,
        'subject_id': chapter.subject_id
    })

@admin_bp.route('/chapter/<int:chapter_id>', methods=['PUT'])
@admin_secure_endpoint(rate_limit_requests=30)
def update_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    data = request.json or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    
    errors = {}
    if not name:
        errors['name'] = 'Name is required.'
    if not description:
        errors['description'] = 'Description is required.'
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    chapter.name = name
    chapter.description = description
    db.session.commit()
    
    return jsonify({'message': 'Chapter updated successfully'})

@admin_bp.route('/chapter/<int:chapter_id>', methods=['DELETE'])
@admin_secure_endpoint(rate_limit_requests=20)
def delete_chapter(chapter_id):
    # Disable CSRF for this specific endpoint
    request.csrf_valid = True
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    try:
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({'message': 'Chapter deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        if 'FOREIGN KEY constraint failed' in str(e):
            return jsonify({'message': 'Cannot delete chapter: It has related quizzes or other data'}), 400
        return jsonify({'message': 'Failed to delete chapter', 'error': str(e)}), 500

@admin_bp.route('/chapters', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def get_chapters():
    try:
        chapters = Chapter.query.order_by(Chapter.id).all()
        
        chapters_list = []
        for chapter in chapters:
            
            questions_list = []
            for quiz in chapter.quizzes:
                for question in quiz.questions:
                    questions_list.append({
                        'id': question.id,
                        'title': question.title,
                        'question_statement': question.question_statement,
                        'option1': question.option1,
                        'option2': question.option2,
                        'option3': question.option3,
                        'option4': question.option4,
                        'correct_option': question.correct_option
                    })
            
            chapters_list.append({
                'id': chapter.id,
                'name': chapter.name,
                'description': chapter.description,
                'subject': {
                    'id': chapter.subject.id,
                    'name': chapter.subject.name
                } if chapter.subject else None,
                'quizzes': [
                    {
                        'id': quiz.id,
                        'chapter_id': quiz.chapter_id,
                        'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                        'time_duration': quiz.time_duration,
                        'remarks': quiz.remarks,
                        'question_count': quiz.question_count
                    }
                    for quiz in chapter.quizzes
                ]
            })
        
        return jsonify({'chapters': chapters_list}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching chapters.'}), 500

@admin_bp.route('/quiz', methods=['POST'])
@admin_secure_endpoint(rate_limit_requests=30)
def create_quiz():
    try:
        data = request.get_json()
        
        chapter_id = data.get('chapter_id')
        date_str = data.get('date')
        duration = data.get('duration')
        
        if not chapter_id or not date_str or not duration:
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Check if chapter exists
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'message': 'Chapter not found'}), 404
        
        # Convert date string to date object
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Check if date is in the future or today
        today = datetime.now(IST).date()
        if date_obj < today:
            return jsonify({'message': 'Please enter date ≥ today'}), 400
        
        # Convert duration to HH:MM format
        duration_hours = duration // 60
        duration_minutes = duration % 60
        time_duration = f"{duration_hours:02d}:{duration_minutes:02d}"
        
        # Create new quiz
        new_quiz = Quiz(
            chapter_id=chapter_id,
            date_of_quiz=date_obj,
            time_duration=time_duration,
            remarks=""
        )
        
        db.session.add(new_quiz)
        db.session.commit()
        
        return jsonify({'message': 'Quiz created successfully', 'quiz_id': new_quiz.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create quiz', 'error': str(e)}), 500

@admin_bp.route('/quiz/<int:quiz_id>', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def get_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz_data = {
            'id': quiz.id,
            'chapter_id': quiz.chapter_id,
            'chapter': {
                'id': quiz.chapter.id,
                'name': quiz.chapter.name
            } if quiz.chapter else None,
            'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
            'time_duration': quiz.time_duration,
            'remarks': quiz.remarks
        }
        return jsonify({'quiz': quiz_data}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching quiz.'}), 500

@admin_bp.route('/quiz/<int:quiz_id>', methods=['PUT'])
@admin_secure_endpoint(rate_limit_requests=30)
def update_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        data = request.get_json()
        
        date_str = data.get('date')
        duration = data.get('duration')
        
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                # Check if date is in the future or today
                today = datetime.now(IST).date()
                if date_obj < today:
                    return jsonify({'message': 'Please enter date ≥ today'}), 400
                quiz.date_of_quiz = date_obj
            except ValueError:
                return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        if duration is not None:
            # Convert duration to HH:MM format
            duration_hours = duration // 60
            duration_minutes = duration % 60
            quiz.time_duration = f"{duration_hours:02d}:{duration_minutes:02d}"
        
        db.session.commit()
        return jsonify({'message': 'Quiz updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update quiz', 'error': str(e)}), 500

@admin_bp.route('/quiz/<int:quiz_id>', methods=['DELETE'])
@admin_secure_endpoint(rate_limit_requests=20)
def delete_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({'message': 'Quiz deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete quiz', 'error': str(e)}), 500

@admin_bp.route('/quizzes', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def get_all_quizzes():
    try:
        quizzes = Quiz.query.order_by(Quiz.id).all()
        
        quizzes_list = []
        for quiz in quizzes:
            
            questions_list = []
            for question in quiz.questions:
                questions_list.append({
                    'id': question.id,
                    'title': question.title,
                    'question_statement': question.question_statement,
                    'option1': question.option1,
                    'option2': question.option2,
                    'option3': question.option3,
                    'option4': question.option4,
                    'correct_option': question.correct_option
                })
            
            quizzes_list.append({
                'id': quiz.id,
                'chapter_id': quiz.chapter_id,
                'chapter_name': quiz.chapter.name if quiz.chapter else 'Unknown Chapter',
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'remarks': quiz.remarks,
                'questions': questions_list
            })
        
        return jsonify({'quizzes': quizzes_list}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching quizzes.'}), 500

@admin_bp.route('/question', methods=['POST'])
@admin_secure_endpoint(rate_limit_requests=30)
def create_question():
    try:
        data = request.get_json()
        
        quiz_id = data.get('quiz_id')
        title = data.get('title')
        question_statement = data.get('question_statement')
        option1 = data.get('option1')
        option2 = data.get('option2')
        option3 = data.get('option3')
        option4 = data.get('option4')
        correct_option = data.get('correct_option')
        
        if not quiz_id or not title or not question_statement or not correct_option:
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Check if quiz exists
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'message': 'Quiz not found'}), 404
        
        # Validate correct_option is between 1 and 4
        try:
            correct_option_int = int(correct_option)
            if correct_option_int < 1 or correct_option_int > 4:
                return jsonify({'message': 'Correct option must be between 1 and 4'}), 400
        except ValueError:
            return jsonify({'message': 'Correct option must be a number between 1 and 4'}), 400
        
        # Create new question
        new_question = Question(
            quiz_id=quiz_id,
            title=title,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option_int
        )
        
        db.session.add(new_question)
        db.session.commit()
        
        return jsonify({'message': 'Question created successfully', 'question_id': new_question.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create question', 'error': str(e)}), 500

@admin_bp.route('/question/<int:question_id>', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def get_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        question_data = {
            'id': question.id,
            'quiz_id': question.quiz_id,
            'title': question.title,
            'question_statement': question.question_statement,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4,
            'correct_option': question.correct_option
        }
        return jsonify({'question': question_data}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching question.'}), 500

@admin_bp.route('/question/<int:question_id>', methods=['PUT'])
@admin_secure_endpoint(rate_limit_requests=30)
def update_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        data = request.get_json()
        
        title = data.get('title')
        question_statement = data.get('question_statement')
        option1 = data.get('option1')
        option2 = data.get('option2')
        option3 = data.get('option3')
        option4 = data.get('option4')
        correct_option = data.get('correct_option')
        
        if title:
            question.title = title
        if question_statement:
            question.question_statement = question_statement
        if option1:
            question.option1 = option1
        if option2:
            question.option2 = option2
        if option3:
            question.option3 = option3
        if option4:
            question.option4 = option4
        if correct_option:
            try:
                correct_option_int = int(correct_option)
                if correct_option_int < 1 or correct_option_int > 4:
                    return jsonify({'message': 'Correct option must be between 1 and 4'}), 400
                question.correct_option = correct_option_int
            except ValueError:
                return jsonify({'message': 'Correct option must be a number between 1 and 4'}), 400
        
        db.session.commit()
        return jsonify({'message': 'Question updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update question', 'error': str(e)}), 500

@admin_bp.route('/question/<int:question_id>', methods=['DELETE'])
@admin_secure_endpoint(rate_limit_requests=20)
def delete_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        
        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete question', 'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def get_users():
    try:
        users = User.query.order_by(User.id).all()
        users_list = [
            {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'qualification': user.qualification,
                'dob': user.dob.isoformat() if user.dob else None,
                'is_admin': user.is_admin
            }
            for user in users
        ]
        return jsonify({'users': users_list}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching users.'}), 500

@admin_bp.route('/search/users', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def search_users():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'results': []}), 200
        
        # Search in name, email, and qualification
        users = User.query.filter(
            db.or_(
                User.full_name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%'),
                User.qualification.ilike(f'%{query}%')
            )
        ).all()
        
        results = []
        for user in users:
            results.append({
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'qualification': user.qualification,
                'dob': user.dob.isoformat() if user.dob else None,
                'is_admin': user.is_admin
            })
        
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while searching users.'}), 500

@admin_bp.route('/summary', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def admin_summary():
    """Get admin summary data with charts and statistics"""
    try:
        from sqlalchemy import func
        
        # Get basic statistics
        total_users = User.query.count()
        total_quizzes = Quiz.query.count()
        total_subjects = Subject.query.count()
        total_attempts = QuizResult.query.count()
        
        # Get subject-wise performance data for bar chart
        subjects = Subject.query.all()
        bar_chart_data = {
            'subjects': [],
            'max_scores': [],
            'min_scores': []
        }
        
        pie_chart_data = {
            'subjects': [],
            'attempts': []
        }
        
        for subject in subjects:
            # Get all quiz results for this subject
            subject_results = db.session.query(QuizResult).join(Quiz).join(Chapter).filter(
                Chapter.subject_id == subject.id
            ).all()
            
            if subject_results:
                scores = [result.score for result in subject_results if result.score is not None]
                if scores:
                    bar_chart_data['subjects'].append(subject.name)
                    bar_chart_data['max_scores'].append(max(scores))
                    bar_chart_data['min_scores'].append(min(scores))
                
                pie_chart_data['subjects'].append(subject.name)
                pie_chart_data['attempts'].append(len(subject_results))
            else:
                # If no results, still show the subject with zero values
                bar_chart_data['subjects'].append(subject.name)
                bar_chart_data['max_scores'].append(0)
                bar_chart_data['min_scores'].append(0)
                
                pie_chart_data['subjects'].append(subject.name)
                pie_chart_data['attempts'].append(0)
        
        return jsonify({
            'summary_stats': {
                'totalUsers': total_users,
                'totalQuizzes': total_quizzes,
                'totalSubjects': total_subjects,
                'totalAttempts': total_attempts
            },
            'bar_chart_data': bar_chart_data,
            'pie_chart_data': pie_chart_data
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'An error occurred while getting summary data.'}), 500

@admin_bp.route('/search/subjects', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def search_subjects():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'results': []}), 200
        
        # Search in name and description
        subjects = Subject.query.filter(
            db.or_(
                Subject.name.ilike(f'%{query}%'),
                Subject.description.ilike(f'%{query}%')
            )
        ).all()
        
        results = []
        for subject in subjects:
            chapters_data = []
            for chapter in subject.chapters:
                quizzes_data = []
                for quiz in chapter.quizzes:
                    quizzes_data.append({
                        'id': quiz.id,
                        'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                        'time_duration': quiz.time_duration
                    })
                
                chapters_data.append({
                    'id': chapter.id,
                    'name': chapter.name,
                    'description': chapter.description,
                    'quizzes': quizzes_data
                })
            
            results.append({
                'id': subject.id,
                'name': subject.name,
                'description': subject.description,
                'chapters': chapters_data
            })
        
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while searching subjects.'}), 500

@admin_bp.route('/search/quizzes', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def search_quizzes():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'results': []}), 200
        
        quizzes = Quiz.query.join(Chapter).join(Subject).filter(
            db.or_(
                Quiz.id.cast(db.String).ilike(f'%{query}%'),
                Chapter.name.ilike(f'%{query}%'),
                Subject.name.ilike(f'%{query}%'),
                Quiz.date_of_quiz.cast(db.String).ilike(f'%{query}%')
            )
        ).all()
        
        results = []
        for quiz in quizzes:
            results.append({
                'id': quiz.id,
                'chapter_name': quiz.chapter.name if quiz.chapter else 'Unknown Chapter',
                'subject_name': quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else 'Unknown Subject',
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'remarks': quiz.remarks
            })
        
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while searching quizzes.'}), 500

@admin_bp.route('/tasks/trigger-daily-reminders', methods=['POST'])
@admin_secure_endpoint(rate_limit_requests=10)
def trigger_daily_reminders():
    """Manually trigger daily quiz reminders"""
    try:
        from backend.tasks import daily_quiz_reminders
        task = daily_quiz_reminders.delay()
        
        return jsonify({
            'status': 'success',
            'message': 'Daily reminders task started',
            'task_id': task.id
        }), 202
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start daily reminders: {str(e)}'
        }), 500

@admin_bp.route('/tasks/trigger-monthly-reports', methods=['POST'])
@admin_secure_endpoint(rate_limit_requests=10)
def trigger_monthly_reports():
    """Manually trigger monthly performance reports"""
    try:
        from backend.tasks import monthly_performance_reports
        task = monthly_performance_reports.delay()
        
        return jsonify({
            'status': 'success',
            'message': 'Monthly reports task started',
            'task_id': task.id
        }), 202
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start monthly reports: {str(e)}'
        }), 500

@admin_bp.route('/tasks/cleanup-exports', methods=['POST'])
@admin_secure_endpoint(rate_limit_requests=10)
def trigger_cleanup_exports():
    """Manually trigger cleanup of old export files"""
    try:
        from backend.tasks import cleanup_old_exports
        task = cleanup_old_exports.delay()
        
        return jsonify({
            'status': 'success',
            'message': 'Cleanup task started',
            'task_id': task.id
        }), 202
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start cleanup: {str(e)}'
        }), 500

@admin_bp.route('/tasks/status/<task_id>', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def get_task_status(task_id):
    """Get status of any task"""
    try:
        from backend.tasks import daily_quiz_reminders, monthly_performance_reports, cleanup_old_exports
        
        # Try to find the task by checking different task types
        task = None
        try:
            task = daily_quiz_reminders.AsyncResult(task_id)
        except:
            pass
        
        if not task or task.state == 'PENDING':
            try:
                task = monthly_performance_reports.AsyncResult(task_id)
            except:
                pass
        
        if not task or task.state == 'PENDING':
            try:
                task = cleanup_old_exports.AsyncResult(task_id)
            except:
                pass
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        if task.ready():
            result = task.get()
            if result and result.get('status') == 'success':
                return jsonify({
                    'status': 'completed',
                    'message': result.get('message', 'Task completed successfully')
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': result.get('message', 'Task failed') if result else 'Task failed'
                }), 500
        else:
            return jsonify({
                'status': 'processing',
                'message': 'Task is still running'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get task status: {str(e)}'
        }), 500

