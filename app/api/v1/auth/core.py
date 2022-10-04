from flask import request, current_app, jsonify, Blueprint
from flask_accept import accept
from pydantic import ValidationError

from app.extensions import bcrypt
from app.api.common.utils.exceptions import InvalidPayloadException, NotFoundException, \
    ServerErrorException, ValidationException
from app.api.common.utils.decorators import authenticate, privileges
from app.models.user import User
from app.api.common.utils.helpers import session_scope
from .validators import UserRegister, UserLogin, PasswordChange, PasswordReset, PasswordRecovery

auth_core_blueprint = Blueprint('auth_core', __name__)

@auth_core_blueprint.route('/auth/register', methods=['POST'])
@accept('application/json')
def register_user():
    """
    New user registration
    """
    # Get post data
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()
    
    # Validate data
    try:
        data = UserRegister(**post_data)
    except ValidationError as err:
        raise ValidationException(err)

    # Create user
    try:
        data = data.dict()

        encrypted_password = bcrypt.generate_password_hash(
            data['password'],
            current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

        data['password'] = encrypted_password
        data.pop('password_confirmation')

        new_user = User(**data)

        email_token = new_user.get_encoded_email_token()
        new_user.email_token_hash = email_token

        # new_user.save()

        if not current_app.testing:
            from app.api.common.utils.mail import send_registration_email
            send_registration_email(new_user, email_token)

        # new_user.save()

        # with session_scope(db.session) as session:
        # session.add(user)

        # with session_scope(db.session) as session:
        # token = user.encode_email_token()
        # user.email_token_hash = bcrypt.generate_password_hash(token, current_app.config.get(
        #     'BCRYPT_LOG_ROUNDS')).decode()

        # if not current_app.testing:
        #     from ....api.common.utils.mails import send_registration_email
        #     send_registration_email(user, token.decode())

        # Generate auth token
        # auth_token = user.encode_auth_token()

        return jsonify(message='Successfully registered.'), 201
    except Exception as err:
        print(err)
        # session.rollback()
        raise ServerErrorException()


@auth_core_blueprint.route('/auth/login', methods=['POST'])
@accept('application/json')
def login_user():
    """
    User login
    """
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()

    try:
        data = UserLogin(**post_data)
    except ValidationError as e:
        raise ValidationException(e)

    user = User.first_by(email=data.email)
    if not user:
        raise NotFoundException(message='User does not exist.')

    if bcrypt.check_password_hash(user.password, data.password):
        auth_token = user.encode_auth_token()
        return jsonify(message='Successfully logged in.', auth_token=auth_token.decode())
    else:
        raise InvalidPayloadException(message="Incorrect password.")


@auth_core_blueprint.route('/auth/logout', methods=['GET'])
@accept('application/json')
# @privileges(role=UserRole.USER | UserRole.ADMIN)
def logout_user(_):
    """
    Logout user
    """
    return jsonify(message='Successfully logged out.')


@auth_core_blueprint.route('/auth/status', methods=['GET'])
@accept('application/json')
@authenticate
def get_user_status(user_id: int):
    """
    Get authentication status
    """
    user = User.get(user_id)
    return jsonify(email=user.email, username=user.username, name=user.name, active=user.active,
                   created_at=user.created_at)


@auth_core_blueprint.route('/auth/password_change', methods=['PUT'])
@accept('application/json')
@authenticate
def password_change(user_id: int):
    """
    Changes user password when logged in
    """
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()
    user = User.get(user_id)
    try:
        data = PasswordChange(user=user, **post_data)
    except ValidationError as e:
        raise ValidationException(e)

    # with session_scope(db.session):
    user.password = bcrypt.generate_password_hash(
        data.new_password,
        current_app.config.get('BCRYPT_LOG_ROUNDS')
    ).decode()

    return jsonify(message='Successfully changed password.')


@auth_core_blueprint.route('/auth/password_reset', methods=['PUT'])
@accept('application/json')
def password_reset():
    """
    Reset user password
    """
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()

    data = PasswordReset(**post_data)
    user_id = User.decode_password_token(data.token)
    user = User.get(user_id)
    if not user or not user.token_hash or not bcrypt.check_password_hash(user.token_hash, data.token):
        raise InvalidPayloadException('Invalid password reset token. Please try again.')

    user.password = bcrypt.generate_password_hash(
        data.password,
        current_app.config.get('BCRYPT_LOG_ROUNDS')
    ).decode()
    user.token_hash = None
    return jsonify(message='Successfully reset password.')


@auth_core_blueprint.route('/auth/password_recovery', methods=['POST'])
@accept('application/json')
def password_recovery():
    """
    Creates a password_recovery_hash and sends email to user
    """
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()

    try:
        data = PasswordRecovery(**post_data)
    except ValidationError as e:
        raise ValidationException(e)

    user = User.first_by(email=data.email)
    if user:
        token = user.encode_password_token()
        user.token_hash = bcrypt.generate_password_hash(token, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        # if not current_app.testing:
            # from project.api.common.utils.mails import send_password_recovery_email
            # send_password_recovery_email(user, token.decode())  # send recovery email
        return jsonify(message='Password recovery email sent.')
    else:
        raise NotFoundException("Email does not exist.")