from celery import shared_task
from .models import TimeSlot
from django.utils import timezone
from datetime import timedelta
from .telegram_service import send_telegram_message

@shared_task
def send_reminder_notifications():
    """Sends reminders about upcoming meetings"""
    now = timezone.now()
    # Слоты которые начнутся в окне 23.5-24.5 часа
    time_24h_from = now + timedelta(hours=23, minutes=30)
    time_24h_to = now + timedelta(hours=24, minutes=30)

    
    slots_24h = TimeSlot.objects.filter(
        is_booked=True,
        start_time__gte=time_24h_from,
        start_time__lte=time_24h_to
    )
    for slot in slots_24h:
        try:
            telegram_profile = slot.owner.profile
            if telegram_profile and telegram_profile.telegram_id:
                message = f"⏰ Reminder! You have a meeting in 24 hours..."
                send_telegram_message(
                    telegram_profile.telegram_id, 
                    message
                )
        except exception as e:
            logging.error(f"Error: {e}")

    return f"Count of free slots: {slots_24h.count()}"
