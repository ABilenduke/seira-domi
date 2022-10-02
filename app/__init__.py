import os
from flask import Config, jsonify, current_app
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from celery import Celery
from .api.common.base_definitions import BaseFlask

from werkzeug.exceptions import HTTPException
from .api.common.error_handling import handle_exception, handle_generic_exception, handle_werkzeug_exception
from .api.common.utils.exceptions import APIException, ServerErrorException, NotFoundException, UnauthorizedException, \
    ForbiddenException, MethodNotAllowedException, NotImplementedException, BadRequestException, InvalidPayloadException

conf = Config(root_path=os.path.abspath(os.path.dirname(__file__)))
conf.from_object(os.getenv('APP_SETTINGS'))

bcrypt = Bcrypt()
mail = Mail()

def create_app(env=None):
    # from app.config import config_by_name
    # from app.routes import register_routes

    app = BaseFlask(__name__)
    bcrypt.init_app(app)
    mail.init_app(app)
    # app.config.from_object(config_by_name[env or "production"])

    # register_routes(api, app)

    from .api.v1.auth import auth_blueprints
    from .api.v1.user import user_blueprints

    blueprints = [*auth_blueprints, *user_blueprints]
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix='/v1')

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

def create_task_queue(app):
    app = app or create_app()
    # add include=['project.tasks.weather_tasks']
    task_queue = Celery(
        __name__,
        broker=app.config['CELERY_BROKER_URL'],
        include=['project.tasks.mail'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    task_queue.conf.update(app.config)
    TaskBase = task_queue.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    task_queue.Task = ContextTask
    return task_queue

task_queue = create_task_queue(current_app)