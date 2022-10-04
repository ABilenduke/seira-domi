from flask import current_app
from flask_mail import Message

from app.extensions import mail
from app import celery


@celery.task
def send_async_registration_email(subject, recipient, text_body, html_body):
    """
    Send registration email asynchronously
    """
    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[recipient]
    )
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


@celery.task
def send_async_password_recovery_email(subject, recipient, text_body, html_body):
    """
    Send password recovery email asynchronously
    """
    msg = Message(subject=subject, recipients=[recipient])
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


@celery.task
def send_async_email_verification_email(subject, recipient, text_body, html_body):
    """
    Send verification email asynchronously
    """
    msg = Message(subject=subject, recipients=[recipient])
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
