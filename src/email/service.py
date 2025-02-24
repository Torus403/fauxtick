from dataclasses import dataclass
from pathlib import Path
from typing import Any

import boto3
from jinja2 import Template

from src.config import settings
from src.user.models import User


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "templates" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    assert settings.emails_enabled, "no provided configuration for email variables"

    ses_client = boto3.client('ses', region_name=settings.AWS_REGION)
    source = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"

    response = ses_client.send_email(
        Source=source,
        Destination={
            "ToAddresses": [email_to],
        },
        Message={
            "Subject": {
                "Data": subject,
                "Charset": "UTF-8",
            },
            "Body": {
                "Html": {
                    "Data": html_content,
                    "Charset": "UTF-8",
                },
            },
        },
    )


def generate_account_confirmation_email(token: str, user: User) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Account Confirmation"
    link = f"{settings.BACKEND_HOST}/confirm-signup?token={token}"
    html_content = render_email_template(
        template_name="account_confirmation.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "valid_hours": settings.CONFIRMATION_TOKEN_EXPIRE_HOURS,
            "link": link,
            "user": user,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_email(token: str, user: User) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password Reset Request"
    link = f"{settings.BACKEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "valid_hours": settings.RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
            "user": user,
        },
    )
    return EmailData(html_content=html_content, subject=subject)
