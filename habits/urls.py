from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, PublicHabitViewSet

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    # Сначала пути роутера (для CRUD привычек)
    path('', include(router.urls)),

    # Затем отдельный путь для публичных привычек (так как это обычный generics.ListAPIView)
    path('public-habits/', PublicHabitViewSet.as_view(), name='public-habit-list'),
]
