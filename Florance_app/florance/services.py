from django.core.mail import send_mail
from django.conf import settings
from .models import Powiadomienie


def notify_user(
    *,
    user,
    tresc,
    link=None,
    send_email=True,
    email_subject="Nowe powiadomienie – Florance"
):
    # 1️⃣ zapis do bazy
    Powiadomienie.objects.create(
        user=user,
        tresc=tresc,
        link=link
    )

    # 2️⃣ email (opcjonalnie)
    if send_email and user.email:
        send_mail(
            subject=email_subject,
            message=f"{tresc}\n\n{link or ''}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
