from django.conf import settings
from django.core.mail import send_mail

# change this to settings.ALLOWED_HOSTS[0] in prod
HOST = "http://127.0.0.1:5000"

EMAIL_TEMPLATE = """
    Hello, {username}, welcome to e-shop store!
    To activate your account and get full access, please click the link below.

    Activation link: {host}/api/auth/activate/{token}

    If you recieved this email by accident, please ignore it. 
    E-shop team.
"""


def send_activation_email(
    username: str,
    user_email: str,
    token: str,
    host: str = HOST,
    email_template: str = EMAIL_TEMPLATE,
    subject: str = "Message from e-shop team!",
):
    message = email_template.format(username=username, token=token, host=host)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.CORPORATE_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
