from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Habit

User = get_user_model()


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='20:00:00',
            action='Принять ванну',
            is_pleasant=True,
            duration=60,
            periodicity=1
        )

    def test_habit_creation(self):
        """Тест: создание привычки проходит успешно."""
        habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Выпить воды',
            duration=60
        )
        self.assertEqual(habit.action, 'Выпить воды')
        self.assertEqual(habit.user, self.user)

    def test_duration_validator(self):
        """Тест: время выполнения не должно превышать 120 секунд."""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Бег',
            duration=150  # Больше 120
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_reward_and_related_habit_validator(self):
        """Тест: нельзя одновременно указывать вознаграждение и связанную привычку."""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Чтение',
            duration=60,
            reward='Съесть конфету',
            related_habit=self.pleasant_habit  # Одновременно и то, и другое
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_pleasant_habit_validator(self):
        """Тест: у приятной привычки не может быть вознаграждения или связанной привычки."""
        habit = Habit(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Поспать',
            is_pleasant=True,
            duration=60,
            reward='Шоколадка'  # Нарушение для приятной привычки
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_related_habit_must_be_pleasant(self):
        """Тест: связанная привычка должна быть приятной."""
        # Создаем полезную привычку (is_pleasant=False)
        useful_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Зарядка',
            duration=60
        )
        # Пытаемся привязать к ней полезную привычку (что неправильно)
        habit = Habit(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Чтение',
            duration=60,
            related_habit=useful_habit
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()
