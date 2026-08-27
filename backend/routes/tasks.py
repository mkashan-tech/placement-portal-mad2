# routes/tasks.py - New file

from flask import Blueprint, jsonify, session
from celery.result import AsyncResult
from extensions import celery

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/status/<task_id>")
def task_status(task_id):
    """Get status of a celery task"""
    if "role" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    task = AsyncResult(task_id, app=celery)
    
    response = {
        "task_id": task_id,
        "status": task.state
    }
    
    if task.state == 'SUCCESS':
        response['result'] = task.result
    elif task.state == 'FAILURE':
        response['error'] = str(task.info)
    
    return jsonify(response)