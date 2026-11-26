from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwner
from .paginators import HabitPagination


class HabitViewSet(viewsets.ModelViewSet):
    """CRUD для привычек текущего пользователя."""
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).order_by('id')

    def get_serializer_context(self):
        # Передаем request (и в нем user) в контекст
        context = super().get_serializer_context()
        return context

    def perform_create(self, serializer):
        # Сохраняем с пользователем
        serializer.save(user=self.request.user)


class PublicHabitViewSet(generics.ListAPIView):  # <--- ИСПОЛЬЗУЕМ generics.ListAPIView
    """Список публичных привычек (только чтение)."""
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]  # Публичный доступ
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).order_by('id')
