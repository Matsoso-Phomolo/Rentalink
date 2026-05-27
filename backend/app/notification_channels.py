from app.models import User


import resend

from app.config import settings


def send_email(to: str, subject: str, message: str) -> bool:
    """
    Send email using Resend.
    """

    try:
        if not settings.resend_api_key:
            print("RESEND_API_KEY missing")
            return False

        resend.api_key = settings.resend_api_key

        response = resend.Emails.send(
            {
                "from": settings.email_from,
                "to": [to],
                "subject": subject,
                "html": f"""
                <div style="font-family: Arial, sans-serif; line-height:1.6;">
                    <h2>LineLink Security</h2>

                    <p>{message}</p>

                    <hr />

                    <p style="font-size:12px;color:#666;">
                        If you did not request this code,
                        please ignore this email.
                    </p>
                </div>
                """,
            }
        )

        print("Email sent:", response)

        return True

    except Exception as exc:
        print("Resend email error:", exc)
        return False


def send_whatsapp(to: str, body: str) -> None:
    # Provider integration point: WhatsApp Business API or local gateway.
    return None


def send_sms(to: str, body: str) -> None:
    # Provider integration point: SMS aggregator.
    return None


def send_password_reset(user: User, token: str, channel: str = "email") -> None:
    message = f"LineLink password reset token: {token}. This token expires in 1 hour."
    if channel == "whatsapp" and user.phone:
        send_whatsapp(user.phone, message)
    elif channel == "sms" and user.phone:
        send_sms(user.phone, message)
    else:
        send_email(user.email, "LineLink password reset", message)


def send_login_credentials(user: User, temporary_password: str) -> None:
    message = f"Your LineLink username is {user.username}. Temporary password: {temporary_password}"
    send_email(user.email, "LineLink account created", message)
    if user.phone:
        send_sms(user.phone, message)
