from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """Кастомная модель пользователя с telegram_chat_id для бота."""
    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Telegram Chat ID'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email or self.username


class Habit(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь'
    )
    place = models.CharField(max_length=255, verbose_name='Место')
    time = models.TimeField(verbose_name='Время выполнения')
    action = models.CharField(max_length=255, verbose_name='Действие')

    # Признак приятной привычки
    is_pleasant = models.BooleanField(default=False, verbose_name='Приятная привычка')

    # Связанная привычка (для полезной)
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Связанная привычка'
    )

    # Периодичность (по умолчанию ежедневная)
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],  # <--- ВАЛИДАТОРЫ ТУТ
        verbose_name='Периодичность (дней)'
    )

    # Вознаграждение
    reward = models.CharField(max_length=255, blank=True, null=True, verbose_name='Вознаграждение')

    # Время на выполнение (в секундах)
    duration = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(120)],  # <--- ВАЛИДАТОРЫ ТУТ
        verbose_name='Время на выполнение (сек)'
    )

    # Признак публичности
    is_public = models.BooleanField(default=False, verbose_name='Публичная привычка')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'

    def __str__(self):
        return f'{self.action} в {self.time} в {self.place}'

    def clean(self):
        # 1. Исключить одновременный выбор связанной привычки и вознаграждения
        if self.related_habit and self.reward:
            raise ValidationError('Нельзя одновременно указывать связанную привычку и вознаграждение.')

        # 2. Время выполнения должно быть не больше 120 секунд (уже есть в валидаторе поля,
        # но продублируем для надежности)
        if self.duration and self.duration > 120:
            raise ValidationError('Время выполнения не должно превышать 120 секунд.')

        # 3. В связанные привычки могут попадать только привычки с признаком приятной
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError('Связанная привычка должна быть приятной.')

        # 4. У приятной привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant:
            if self.reward or self.related_habit:
                raise ValidationError('У приятной привычки не может быть вознаграждения или связанной привычки.')

        # 5. Нельзя выполнять привычку реже, чем 1 раз в 7 дней
        if self.periodicity < 1 or self.periodicity > 7:
            raise ValidationError('Периодичность должна быть от 1 до 7 дней.')
