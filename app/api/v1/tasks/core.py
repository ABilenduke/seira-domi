from flask import Blueprint, jsonify
from flask_accept import accept
from app.tasks.mail import send_async_registration_email

tasks_core_blueprint = Blueprint('tasks_core', __name__)

@tasks_core_blueprint.route('/tasks', methods=['GET'])
@accept('application/json')
def get_tasks():
    """
    Get all tasks
    """
    try:
        print('hi')
        print(send_async_registration_email.get())
    except Exception as err:
        print(err)
    
    return jsonify(message='get tasks')