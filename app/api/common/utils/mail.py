from flask import render_template, request, url_for, current_app

from app.tasks.mail import send_async_registration_email, send_async_password_recovery_email,\
    send_async_email_verification_email

def send_registration_email(user, token):
    """
    Send email for registration
    """
    url_root = "https://flask-redis.test/auth/register?r=" + token # request.url_root
    href = url_root + url_for('email_verification.verify_email', token='')[1:] + token
    app_name = current_app.config.get('APP_NAME')
    send_async_registration_email.delay(
        subject=f'Welcome to {app_name}!',
        recipient=user.email,
        text_body=render_template(
            "auth/new_registration.txt",
            user=user
        ),
        html_body=render_template(
            "auth/new_registration.html",
            user=user,
            href=href
        )
    )

def send_email_verification_email(user, token):
    """
    Send email for verification
    """
    url_root = "https://backend.flask-redis.test/" # request.url_root
    href = url_root + token
    app_name = current_app.config.get('APP_NAME')
    send_async_email_verification_email.delay(
        subject=f'Email confirmation for {app_name}',
        recipient=user.email,
        text_body=render_template(
            "auth/email_verification.txt",
            user=user
        ),
        html_body=render_template(
            "auth/email_verification.html",
            user=user,
            href=href
        )
    )