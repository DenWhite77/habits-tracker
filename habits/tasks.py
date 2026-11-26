import requests
from celery import shared_task
from django.conf import settings
from .models import Habit


@shared_task
def send_habit_reminder(habit_id):
    try:
        habit = Habit.objects.get(id=habit_id)
        user = habit.user

        if not user.telegram_chat_id:
            return "У пользователя нет chat_id"

        message = (
            f"⏰ Напоминание!\n"
            f"Пора выполнить привычку: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Время: {habit.time}"
        )

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': user.telegram_chat_id,
            'text': message
        }
        response = requests.post(url, data=payload)
        return f"Отправлено: {response.status_code}"
    except Exception as e:
        return f"Ошибка: {e}"
