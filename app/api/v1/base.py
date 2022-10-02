from flask import request, current_app, jsonify
from pydantic import BaseModel, ValidationError
from typing import Type

from ..common.utils.exceptions import NotFoundException, InvalidPayloadException, BadRequestException, ValidationException
from ..common.utils.helpers import get_query_from_text, session_scope

class BaseAPI:
    def post(
        self,
        logged_in_user_id: int,
        # validator: Type[BaseModel],
        # entity: Type[Base],
        post_data: dict = None
    ):
        """
        Standard POST call
        """
        post_data = dict(post_data or request.get_json())

        if not post_data:
            raise InvalidPayloadException()
        try:
            # with session_scope() as session:
            try:
                data = validator(logged_in_user_id=logged_in_user_id, **post_data)
            except ValidationError as e:
                raise ValidationException(e)

            model = entity(**data.dict())
            model.save()
            return jsonify(message=f'{entity.__tablename__} was added'), 201
        except Exception as err:
            raise InvalidPayloadException()