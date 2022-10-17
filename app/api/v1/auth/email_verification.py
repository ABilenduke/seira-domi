from datetime import datetime
from flask import current_app, jsonify, Blueprint
from flask_accept import accept

from app.extensions import bcrypt
from app.api.common.utils.exceptions import NotFoundException, InvalidPayloadException
from app.api.common.utils.decorators import authenticate
from app.models.user import User

email_verification_blueprint = Blueprint('email_verification', __name__)


@email_verification_blueprint.route('/email_verification/', methods=['GET'])
@accept('application/json')
@authenticate
def email_verification(user_id: int):
    """
    Creates a email_token_hash and sends email with token to user
    """
    # fetch the user data
    user = User.first(User.id == user_id)
    if user:
        token = user.encode_email_token()
        user.email_token_hash = bcrypt.generate_password_hash(token, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()

        if not current_app.testing:
            from ....api.common.utils.mail import send_email_verification_email
            send_email_verification_email(user, token.decode())
        return jsonify(message='sent email with verification token')


@email_verification_blueprint.route('/email_verification/<token>', methods=['GET'])
def verify_email(token):
    """
    Verifies email with given token
    """
    print('HI!')
    user_id = User.decode_email_token(token)
    print(user_id)
    # user = User.get(user_id)
    # if not user:
    #     raise NotFoundException(message='user does not exist')
    # if not user.email_token_hash:
    #     raise InvalidPayloadException(message='verification link expired')

    # bcrypt.check_password_hash(user.email_token_hash, token)

    # user.email_validation_date = datetime.utcnow()
    # user.active = True
    # user.email_token_hash = None

    return jsonify(message='email verified')


@email_verification_blueprint.route('/email_verification/resend', methods=['GET'])
@accept('application/json')
@authenticate
def resend_verification(user_id: int):
    """
    Resend verification email
    """
    user = User.first(User.id == user_id)
    if user:
        token = user.encode_email_token()
        user.email_token_hash = bcrypt.generate_password_hash(token, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        
        if not current_app.testing:
            from ....api.common.utils.mail import send_registration_email
            send_registration_email(user, token.decode())
        return jsonify(message="verification email resent")