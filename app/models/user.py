from __future__ import annotations
import jwt
from flask import current_app
import json
from enum import Enum, IntFlag
from typing import Optional
from datetime import datetime, timedelta
from redis_om import JsonModel, Field

from app.extensions import bcrypt
from app.api.common.utils.exceptions import UnauthorizedException, BadRequestException

class SocialAuth(Enum):
    """
    Social authentication providers
    """
    FACEBOOK = 'Facebook'
    GITHUB = 'GitHub'

class User(JsonModel):
    """
    User model
    """
    name: str
    email: str = Field(index=True)
    username: str = Field(index=True)
    password: str
    token_hash: Optional[str] = None
    email_token_hash: Optional[str] = None
    email_validation_date: Optional[datetime] = None

    # Social
    social_id: Optional[str] = None
    social_type: Optional[str] = None
    social_access_token: Optional[str] = None

    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
    deleted_at: Optional[datetime] = None

    @classmethod
    def exists(cls, *criterion) -> bool:
        """
        Get first entity that matches to criterion
        """
        result = cls.find(*criterion).all()
        return len(result) > 0

    # def json(self) -> json:
    #     """
    #     Get model data in JSON format
    #     """
    #     return {
    #         'pk': self.pk,
    #         'name': self.name,
    #         'email': self.email,
    #         'username': self.username,
    #         'created_at': self.created_at,
    #         'updated_at': self.updated_at,
    #         'deleted_at': self.deleted_at,
    #     }

    # @classmethod
    # def get_by_role(cls, role: UserRole) -> User:
    #     """
    #     Get
    #     """
    #     pass

    def encode_auth_token(self) -> bytes:
        """
        Generates the auth token
        """
        payload = {
            'exp': datetime.utcnow() + timedelta(
                days=current_app.config['TOKEN_EXPIRATION_DAYS'],
                seconds=current_app.config['TOKEN_EXPIRATION_SECONDS']),
            'iat': datetime.utcnow(),
            'sub': self.pk
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    
    @staticmethod
    def decode_auth_token(auth_token: str) -> int:
        """
        Decodes the auth token - :param auth_token: - :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException(message='Signature expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise UnauthorizedException(message='Invalid token. Please log in again.')
    
    def encoded_email_token(self) -> bytes:
        """
        Generates the email token
        """
        payload = {
            'exp': datetime.utcnow() + timedelta(
                days=current_app.config['TOKEN_EMAIL_EXPIRATION_DAYS'],
                seconds=current_app.config['TOKEN_EMAIL_EXPIRATION_SECONDS']),
            'iat': datetime.utcnow(),
            'sub': self.pk
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_email_token(email_token: str) -> int:
        """
        Decodes the email token - :param auth_token: - :return: integer|string
        """
        try:
            payload = jwt.decode(email_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise BadRequestException(message='Email recovery token expired. Please try again.')
        except jwt.InvalidTokenError:
            raise BadRequestException(message='Invalid email verification token. Please try again.')
