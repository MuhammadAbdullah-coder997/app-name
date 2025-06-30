from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Reading, User

# 🔔 Triggered when a new Reading is created
@receiver(post_save, sender=Reading)
def notify_if_abnormal(sender, instance, created, **kwargs):
    if created:
        systolic = instance.systolic
        diastolic = instance.diastolic
        glucose = instance.glucose_level

        is_abnormal_bp = systolic >= 140 or diastolic >= 90
        is_abnormal_glucose = glucose >= 200

        if is_abnormal_bp or is_abnormal_glucose:
            # You can change this to send an email or push notification
            print(f"[Warning] Abnormal reading for {instance.user.email}")

            # Example: Send email notification (requires email backend configured)
            try:
                send_mail(
                    subject='Abnormal Health Reading Alert',
                    message=(
                        f"Hi {instance.user.get_full_name() or 'User'},\n\n"
                        f"An abnormal health reading was recorded:\n"
                        f"- Blood Pressure: {systolic}/{diastolic}\n"
                        f"- Glucose: {glucose} {instance.glucose_unit}\n\n"
                        "Please consult your doctor if necessary."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"[Error] Failed to send alert email: {e}")


# 🆕 Log new user creation
@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        print(f"[User Created] New user registered: {instance.email}")
