from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.ai_service import chat_response, evaluate_descriptive, generate_questions

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json() or {}
    reply = chat_response(
        topic_id=data.get('topic_id'),
        subject_id=data.get('subject_id'),
        message=data.get('message', ''),
        context=data.get('context', '')
    )
    return jsonify(reply)

@ai_bp.route('/evaluate', methods=['POST'])
@login_required
def evaluate():
    data = request.get_json() or {}
    if data.get('type') == 'descriptive':
        result = evaluate_descriptive(data.get('question', ''), data.get('answer', ''))
    else:
        from app.services.ai_service import evaluate_mcq_wrong
        result = evaluate_mcq_wrong(data.get('question', ''), data.get('correct_answer', ''))
    return jsonify(result)

@ai_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    data = request.get_json() or {}
    questions = generate_questions(
        subject_name=data.get('subject', ''),
        topic=data.get('topic', ''),
        difficulty=data.get('difficulty', 'medium'),
        count=int(data.get('count', 3)),
        q_type=data.get('type', 'mcq')
    )
    return jsonify({'questions': questions})
