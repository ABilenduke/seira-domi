import datetime, os, logging
from flask import Flask, jsonify, Response
from flask.json import JSONEncoder
from flask_cors import CORS

class BaseJsonEncoder(JSONEncoder):
    """
    Encodes JSON
    """
    def default(self, obj):
        try:
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

class BaseResponse(Response):
    """
    Base Response
    """
    default_mimetype = 'application/json'

    @classmethod
    def force_type(cls, response, environ=None):
        """
        Force type
        """
        if isinstance(response, dict):
            response = jsonify(response)
        return super(BaseResponse, cls).force_type(response, environ)
    
class BaseFlask(Flask):
    """
    Base Flask
    """
    response_class = BaseResponse
    json_encoder = BaseJsonEncoder

    def __init__(self, import_name):
        Flask.__init__(
            self,
            import_name,
            static_folder='./static',
            template_folder='./templates'
        )
        #set config
        app_settings = os.getenv('APP_SETTINGS')
        self.config.from_object(app_settings)

        # configure logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            filename=self.config['LOGGING_LOCATION'],
            mode='a',
            maxBytes=1024 * 1024 * 100,
            backupCount=20
        )
        file_handler.setFormatter(
            logging.Formatter(self.config['LOGGING_FORMAT']))
        self.logger.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

        # enable CORS
        CORS(self, resources={r"/*": {"origins": "*"}})