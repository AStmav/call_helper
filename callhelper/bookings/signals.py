"""
Django Signals для автоматической отправки уведомлений в Telegram

Signals позволяют выполнять код при определенных событиях в Django.
В данном случае - отправка уведомлений при бронировании/отмене.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import TimeSlot
from .telegram_service import (
    send_telegram_message,
    format_booking_notification,
    format_cancellation_notification
)
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=TimeSlot)
def track_booking_status_before_save(sender, instance, **kwargs):
    """
    Сохраняет предыдущее состояние до сохранения для отслеживания изменений
    """
    if instance.pk:
        try:
            old_instance = TimeSlot.objects.get(pk=instance.pk)
            instance._old_is_booked = old_instance.is_booked
            instance._old_booked_by = old_instance.booked_by
        except TimeSlot.DoesNotExist:
            instance._old_is_booked = False
            instance._old_booked_by = None
    else:
        instance._old_is_booked = False
        instance._old_booked_by = None


@receiver(post_save, sender=TimeSlot)
def send_booking_telegram_notification(sender, instance, created, **kwargs):
    """
    Отправляет уведомление в Telegram при бронировании слота
    
    sender - модель, которая вызвала сигнал (TimeSlot)
    instance - конкретный объект TimeSlot, который был сохранен
    created - True если объект создан впервые, False если обновлен
    """
    # Проверяем, стал ли слот забронированным (is_booked изменился с False на True)
    was_booked_before = getattr(instance, '_old_is_booked', False)
    
    if instance.is_booked and not was_booked_before:
        # Слот только что был забронирован - отправляем уведомление владельцу
        try:
            profile = instance.owner.profile
            if profile and profile.telegram_id:
                message = format_booking_notification(instance, is_owner=True)
                send_telegram_message(
                    chat_id=profile.telegram_id,
                    message=message
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления владельцу: {e}")
    
    # Проверяем, было ли бронирование отменено
    elif was_booked_before and not instance.is_booked:
        # Бронирование было отменено - отправляем уведомление
        try:
            profile = instance.owner.profile
            if profile and profile.telegram_id:
                message = format_cancellation_notification(instance)
                send_telegram_message(
                    chat_id=profile.telegram_id,
                    message=message
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления об отмене: {e}")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Автоматически создает профиль для нового пользователя
    """
    if created:
        from .models import UserProfile
        UserProfile.objects.get_or_create(user=instance)

