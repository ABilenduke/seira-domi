import os
from flask import Config, jsonify, url_for
from celery import Celery
from app.extensions import mail, bcrypt
from .api.common.base_definitions import BaseFlask
from werkzeug.exceptions import HTTPException
from .api.common.error_handling import handle_exception, handle_generic_exception, handle_werkzeug_exception
from .api.common.utils.exceptions import APIException, ServerErrorException, NotFoundException, UnauthorizedException, \
    ForbiddenException, MethodNotAllowedException, NotImplementedException, BadRequestException, InvalidPayloadException

conf = Config(root_path=os.path.abspath(os.path.dirname(__file__)))
conf.from_object(os.getenv('APP_SETTINGS'))

import time
import random

def create_app(**kwargs):
    app = BaseFlask(__name__)

    bcrypt.init_app(app)
    mail.init_app(app)

    if kwargs.get('celery'):
        init_celery(kwargs.get('celery'), app)

    from .api.v1.auth import auth_blueprints
    from .api.v1.user import user_blueprints
    from .api.v1.tasks import tasks_blueprints

    blueprints = [*auth_blueprints, *user_blueprints, *tasks_blueprints]
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix='/v1')

    @celery.task(bind=True)
    def long_task(self):
        """Background task that runs a long function with progress reports."""
        verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
        adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
        noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
        message = ''
        total = random.randint(10, 50)
        for i in range(total):
            if not message or random.random() < 0.25:
                message = '{0} {1} {2}...'.format(random.choice(verb),
                                                random.choice(adjective),
                                                random.choice(noun))
            self.update_state(state='PROGRESS',
                            meta={'current': i, 'total': total,
                                    'status': message})
            time.sleep(1)
        return {'current': 100, 'total': 100, 'status': 'Task completed!',
                'result': 42}
    
    @app.route('/longtask', methods=['POST'])
    def longtask():
        task = long_task.apply_async()
        return jsonify({'Location': url_for('taskstatus',
                                                    task_id=task.id)}), 202
    
    @app.route('/status/<task_id>')
    def taskstatus(task_id):
        task = long_task.AsyncResult(task_id)
        print(task)
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
            }
            if 'result' in task.info:
                response['result'] = task.info['result']
        else:
            # something went wrong in the background job
            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'status': str(task.info),  # this is the exception raised
            }
        return jsonify(response)

    @app.route("/health")
    def health():
        return jsonify("healthy")

    app.register_error_handler(InvalidPayloadException, handle_exception)
    app.register_error_handler(BadRequestException, handle_exception)
    app.register_error_handler(UnauthorizedException, handle_exception)
    app.register_error_handler(ForbiddenException, handle_exception)
    app.register_error_handler(NotFoundException, handle_exception)
    app.register_error_handler(ServerErrorException, handle_exception)
    app.register_error_handler(Exception, handle_generic_exception)
    app.register_error_handler(HTTPException, handle_werkzeug_exception)

    return app

def make_celery(app_name=__name__):
    broker_uri = os.getenv('CELERY_BROKER_URL')
    backend_uri = os.getenv('CELERY_RESULT_BACKEND')

    return Celery(
        app_name,
        broker=broker_uri,
        backend=backend_uri,
        include=['app.tasks']
    )

def init_celery(celery, app):
    celery.conf.update({
        'broker_url': os.getenv('CELERY_BROKER_URL'),
        'result_backend': os.getenv('CELERY_RESULT_BACKEND'),
        'imports': ("app.tasks"),
        # 'task_serializer': 'json',
        # 'result_serializer': 'json',
    })
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

celery = make_celery()


