from flask import request, jsonify
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource, fields
from flask.wrappers import Response
from typing import List
from .model import User
from pydantic import ValidationError

api = Namespace("User", description="A modular namespace within user")  # noqa

model = api.model('Model', {
    'name': fields.String,
    'email': fields.String,
})

@api.route("/")
class UserResource(Resource):
    """Users"""

    def get(self):
        """Fetch a Single User"""
        try:
            return 'hello'

        except Exception as e:
            print(e)
            return "Bad request."
            
    def put(self):
        """Create a Single User"""
        try:
            print(request)
            new_user = User(**request.get_json())
            new_user.save()
            return {'message': 'created successfully', 'user': new_user.pk}, 201

        except Exception as e:
            print(e)
            return "Bad request.", 400
