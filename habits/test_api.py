from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Habit

User = get_user_model()


class HabitAPITest(APITestCase):
    def setUp(self):
        # Создаем двух пользователей
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')

        # Создаем привычку для user1
        self.habit1 = Habit.objects.create(
            user=self.user1,
            place='Дом',
            time='08:00:00',
            action='Выпить воды',
            duration=60,
            is_public=False
        )

        # Создаем публичную привычку
        self.public_habit = Habit.objects.create(
            user=self.user1,
            place='Парк',
            time='18:00:00',
            action='Пробежка',
            duration=120,
            is_public=True
        )

        # URL-адреса
        self.list_url = reverse('habit-list')
        self.detail_url = reverse('habit-detail', kwargs={'pk': self.habit1.pk})

    def test_unauthorized_access(self):
        """Тест: неавторизованный пользователь не может получить доступ."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_own_habits(self):
        """Тест: пользователь видит только свои привычки (не публичные)."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # В списке должна быть только 1 его личная привычка (public_habit в другом эндпоинте)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['action'], 'Выпить воды')

    def test_user_cannot_edit_others_habit(self):
        """Тест: пользователь не может редактировать чужую привычку."""
        self.client.force_authenticate(user=self.user2)  # Заходим под вторым юзером
        response = self.client.patch(self.detail_url, {'action': 'Хакнуто'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Или 403, в
        # зависимости от настройки queryset

    def test_public_habits_list(self):
        """Тест: публичные привычки видны всем авторизованным."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('public-habit-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['action'], 'Пробежка')

    def test_create_habit(self):
        """Тест: создание привычки."""
        self.client.force_authenticate(user=self.user1)
        data = {
            "place": "Офис",
            "time": "12:00:00",
            "action": "Размяться",
            "duration": 60,
            "periodicity": 1
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 3)  # Было 2, стало 3
