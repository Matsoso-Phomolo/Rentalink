import requests

from app.config import settings
from app.models import User


def send_email(to_email: str, subject: str, message: str) -> bool:
    """
    Send email using Resend API.
    """

    if not settings.resend_api_key:
        print("RESEND_API_KEY missing")
        return False

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.email_from,
                "to": [to_email],
                "subject": subject,
                "html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>LineLink Security</h2>
                    <p>{message}</p>
                </div>
                """,
            },
            timeout=20,
        )

        print("EMAIL STATUS:", response.status_code)
        print("EMAIL RESPONSE:", response.text)

        return response.status_code in [200, 201]

    except Exception as exc:
        print("EMAIL ERROR:", str(exc))
        return False


def send_sms(phone: str, message: str) -> bool:
    """
    Placeholder SMS sender.
    """

    print(f"SMS to {phone}: {message}")
    return True


def send_whatsapp(phone: str, message: str) -> bool:
    """
    Placeholder WhatsApp sender.
    """

    print(f"WhatsApp to {phone}: {message}")
    return True


def send_password_reset(user: User, token: str, channel: str = "email") -> bool:
    """
    Send password reset notification.
    """

    reset_link = (
        f"{settings.public_base_url}/#/reset-password?token={token}"
    )

    message = (
        "You requested a password reset.<br><br>"
        f"Reset link:<br>"
        f"<a href='{reset_link}'>{reset_link}</a><br><br>"
        "If you did not request this reset, ignore this email."
    )

    if channel == "sms" and user.phone:
        return send_sms(user.phone, reset_link)

    if channel == "whatsapp" and user.phone:
        return send_whatsapp(user.phone, reset_link)

    return send_email(
        user.email,
        "LineLink Password Reset",
        message,
    )


def send_login_credentials(user: User, temporary_password: str) -> None:
    
    message = (
        f"Your LineLink username is {user.username}. "
        f"Temporary password: {temporary_password}"
    )

    send_email(
        user.email,
        "LineLink account created",
        message,
    )
    send_email(user.email, "LineLink account created", message)
    if user.phone:
        send_sms(user.phone, message)
        send_whatsapp(user.phone, message)
