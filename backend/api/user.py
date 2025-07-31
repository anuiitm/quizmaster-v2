from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from backend.models.model import Quiz, Chapter, Subject, QuizResult
from datetime import datetime
from flask import request
from backend.extensions import db
from backend.utils.decorators import secure_endpoint, user_context_middleware
import os

user_bp = Blueprint('user', __name__)

@user_bp.route('/quizzes', methods=['GET'])
@secure_endpoint(rate_limit_requests=60)
def get_user_quizzes():
    try:
        # Get all quizzes (no date filter)
        quizzes = Quiz.query.order_by(Quiz.date_of_quiz).all()
        quizzes_list = []
        for quiz in quizzes:
            quizzes_list.append({
                'id': quiz.id,
                'questions': [{'id': q.id} for q in quiz.questions],
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'chapter': {
                    'id': quiz.chapter.id,
                    'name': quiz.chapter.name,
                    'subject': {
                        'id': quiz.chapter.subject.id,
                        'name': quiz.chapter.subject.name
                    } if quiz.chapter and quiz.chapter.subject else None
                } if quiz.chapter else None
            })
        # Get quiz IDs already taken by the user
        taken_quiz_ids = [result.quiz_id for result in QuizResult.query.filter_by(user_id=current_user.id).all()]
        return jsonify({'all_quizzes': quizzes_list, 'taken_quiz_ids': taken_quiz_ids}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching quizzes.'}), 500

@user_bp.route('/quiz/<int:quiz_id>', methods=['GET'])
@secure_endpoint(rate_limit_requests=60)
def get_quiz_for_user(quiz_id):
    from backend.models.model import Quiz
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz_data = {
        'id': quiz.id,
        'chapter_id': quiz.chapter_id,
        'chapter': {
            'id': quiz.chapter.id,
            'name': quiz.chapter.name,
            'subject': {
                'id': quiz.chapter.subject.id,
                'name': quiz.chapter.subject.name
            } if quiz.chapter and quiz.chapter.subject else None
        } if quiz.chapter else None,
        'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
        'time_duration': quiz.time_duration,
        'remarks': quiz.remarks,
        'questions': [
            {
                'id': q.id,
                'title': q.title,
                'question_statement': q.question_statement,
                'option1': q.option1,
                'option2': q.option2,
                'option3': q.option3,
                'option4': q.option4,
                'correct_option': q.correct_option
            } for q in quiz.questions
        ]
    }
    return jsonify({'quiz': quiz_data}), 200

@user_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@secure_endpoint(rate_limit_requests=10)
def submit_quiz_result(quiz_id):
    from backend.models.model import QuizResult, Quiz
    # Prevent multiple attempts
    existing = QuizResult.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    if existing:
        return jsonify({'message': 'Quiz already submitted'}), 400
    data = request.get_json()
    score = data.get('score')
    if score is None:
        return jsonify({'message': 'Score is required'}), 400
    quiz = Quiz.query.get_or_404(quiz_id)
    result = QuizResult(user_id=current_user.id, quiz_id=quiz_id, score=score)
    from backend.extensions import db
    db.session.add(result)
    db.session.commit()
    return jsonify({'message': 'Quiz submitted', 'score': score}), 200

@user_bp.route('/scores', methods=['GET'])
@secure_endpoint(rate_limit_requests=60)
def get_user_scores():
    try:
        from backend.models.model import QuizResult, Quiz, Chapter, Subject
        
        results = db.session.query(QuizResult, Quiz, Chapter, Subject).join(
            Quiz, QuizResult.quiz_id == Quiz.id
        ).join(
            Chapter, Quiz.chapter_id == Chapter.id
        ).join(
            Subject, Chapter.subject_id == Subject.id
        ).filter(
            QuizResult.user_id == current_user.id
        ).order_by(QuizResult.date_taken.desc()).all()
        
        scores = []
        for result, quiz, chapter, subject in results:
            scores.append({
                'id': result.id,
                'quiz_id': quiz.id,
                'subject_name': subject.name,
                'chapter_name': chapter.name,
                'score': result.score,
                'date_taken': result.date_taken.isoformat() if result.date_taken else None
            })
        
        return jsonify({'scores': scores}), 200
        
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching scores.'}), 500

@user_bp.route('/summary', methods=['GET'])
@secure_endpoint(rate_limit_requests=60)
def user_summary():
    from backend.models.model import QuizResult
    from collections import defaultdict
    # Subject-wise attempts
    subject_counts = defaultdict(int)
    results = QuizResult.query.filter_by(user_id=current_user.id).all()
    for r in results:
        if r.quiz and r.quiz.chapter and r.quiz.chapter.subject:
            subject_counts[r.quiz.chapter.subject.name] += 1
    subjects = list(subject_counts.keys())
    attempt_counts = [subject_counts[s] for s in subjects]
    # Month-wise attempts
    month_counts = defaultdict(int)
    for r in results:
        if r.date_taken:
            month = r.date_taken.strftime('%B')
            month_counts[month] += 1
    months = list(month_counts.keys())
    attempts = [month_counts[m] for m in months]
    return jsonify({
        'bar_chart_data': {'subjects': subjects, 'attempt_counts': attempt_counts},
        'pie_chart_data': {'months': months, 'attempts': attempts}
    })

@user_bp.route('/search', methods=['GET'])
@login_required
def user_search():
    query = request.args.get('q', '').strip().lower()
    from backend.models.model import Quiz, Subject, QuizResult, Chapter
    results = []
    quiz_results = {}

    # Find quizzes matching query - use correct relationship syntax
    quiz_objs = Quiz.query.join(Chapter).join(Subject).filter(
        (Quiz.id.cast(db.String).ilike(f'%{query}%')) |
        (Chapter.name.ilike(f'%{query}%')) |
        (Subject.name.ilike(f'%{query}%'))
    ).all()
    
    for quiz in quiz_objs:
        # Access subject through the chapter relationship
        subject_name = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else 'Unknown Subject'
        results.append({
            'id': quiz.id,
            'title': f"Quiz {quiz.id} - {quiz.chapter.name if quiz.chapter else 'Unknown Chapter'}",
            'description': f"Subject: {subject_name} | Date: {quiz.date_of_quiz.strftime('%Y-%m-%d') if quiz.date_of_quiz else 'No date'}",
            'type': 'quiz',
            'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else '',
            'chapter': {
                'id': quiz.chapter.id,
                'name': quiz.chapter.name,
                'subject': {
                    'id': quiz.chapter.subject.id,
                    'name': quiz.chapter.subject.name
                } if quiz.chapter and quiz.chapter.subject else None
            } if quiz.chapter else None
        })

    # Find subjects matching query
    subject_objs = Subject.query.filter(Subject.name.ilike(f'%{query}%')).all()
    for subject in subject_objs:
        chapters = []
        for chapter in subject.chapters:
            quizzes_in_chapter = []
            for quiz in chapter.quizzes:
                quizzes_in_chapter.append({
                    'id': quiz.id,
                    'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else ''
                })
            chapters.append({
                'id': chapter.id,
                'name': chapter.name,
                'quizzes': quizzes_in_chapter
            })
        
        results.append({
            'id': subject.id,
            'title': f"Subject: {subject.name}",
            'description': f"{subject.description or 'No description'} | Chapters: {len(subject.chapters)} | Total Quizzes: {sum(len(chapter.quizzes) for chapter in subject.chapters)}",
            'type': 'subject',
            'name': subject.name,
            'description_full': subject.description,
            'chapters': chapters
        })

    # Quiz results for this user
    user_results = QuizResult.query.filter_by(user_id=current_user.id).all()
    for r in user_results:
        quiz_results[r.quiz_id] = r.score

    return jsonify({
        'results': results,
        'quiz_results': quiz_results
    })
