from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from .models import Habit
from .tasks import send_habit_reminder

User = get_user_model()


class TaskTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='taskuser',
            password='pass123',
            telegram_chat_id='123456789'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Тестовая привычка',
            duration=60
        )

    @patch('habits.tasks.requests.post')
    def test_send_habit_reminder(self, mock_post):
        """Тест: задача отправляет запрос в Telegram."""
        # Настраиваем мок, чтобы он вернул успешный ответ
        mock_post.return_value.status_code = 200

        result = send_habit_reminder(self.habit.id)

        # Проверяем, что requests.post был вызван
        self.assertTrue(mock_post.called)
        self.assertIn('Отправлено: 200', result)

    def test_send_habit_reminder_no_chat_id(self):
        """Тест: если у пользователя нет chat_id, задача не отправляет сообщение."""
        self.user.telegram_chat_id = None
        self.user.save()

        result = send_habit_reminder(self.habit.id)
        self.assertIn('У пользователя нет chat_id', result)
