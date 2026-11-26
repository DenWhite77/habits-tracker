from rest_framework import serializers
from .models import Habit
from django.core.exceptions import ValidationError as DjangoValidationError


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user',)

    def validate(self, attrs):
        # Берем пользователя из контекста запроса
        request = self.context.get('request')
        user = request.user if request else None

        # Создаем или обновляем экземпляр для валидации
        if self.instance:
            instance = Habit(**attrs, id=self.instance.id)
        else:
            instance = Habit(**attrs)

        # Подставляем пользователя, чтобы full_clean() не ругался
        if user:
            instance.user = user

        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs
