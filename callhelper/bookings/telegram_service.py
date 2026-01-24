"""
Telegram Bot Service для отправки уведомлений

Этот модуль содержит функции для работы с Telegram Bot API
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, message, parse_mode='HTML'):
    """
    Отправляет сообщение в Telegram
    
    Args:
        chat_id (int): Telegram ID пользователя или чата
        message (str): Текст сообщения
        parse_mode (str): Форматирование ('HTML' или 'Markdown')
    
    Returns:
        bool: True если сообщение отправлено успешно, False в случае ошибки
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    
    if not bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN не настроен в settings.py")
        return False
    
    if not chat_id:
        logger.warning("chat_id не указан, невозможно отправить сообщение")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': parse_mode
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Сообщение успешно отправлено в Telegram chat_id: {chat_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")
        return False


def format_booking_notification(slot, is_owner=True):
    """
    Форматирует уведомление о бронировании для Telegram
    
    Args:
        slot (TimeSlot): Объект слота
        is_owner (bool): True если уведомление для владельца, False для гостя
    
    Returns:
        str: Отформатированное сообщение
    """
    if is_owner:
        # Уведомление для владельца слота
        booked_by = slot.booked_by.username if slot.booked_by else slot.guest_name
        message = f"""
📅 <b>Новое бронирование!</b>

⏰ <b>Время:</b> {slot.start_time.strftime('%d.%m.%Y %H:%M')} - {slot.end_time.strftime('%H:%M')}
👤 <b>Забронировано:</b> {booked_by}
⏱️ <b>Длительность:</b> {slot.get_duration_display()}
"""
        if slot.session:
            message += f"📋 <b>Сессия:</b> {slot.session.title}\n"
        
        return message.strip()
    else:
        # Уведомление для гостя
        message = f"""
✅ <b>Бронирование подтверждено!</b>

⏰ <b>Ваше время:</b> {slot.start_time.strftime('%d.%m.%Y %H:%M')} - {slot.end_time.strftime('%H:%M')}
⏱️ <b>Длительность:</b> {slot.get_duration_display()}
👤 <b>С кем:</b> {slot.owner.username}
"""
        if slot.session and slot.session.description:
            message += f"📝 {slot.session.description}\n"
        
        return message.strip()


def format_cancellation_notification(slot):
    """
    Форматирует уведомление об отмене бронирования
    """
    message = f"""
❌ <b>Бронирование отменено</b>

⏰ <b>Время:</b> {slot.start_time.strftime('%d.%m.%Y %H:%M')} - {slot.end_time.strftime('%H:%M')}
"""
    return message.strip()

