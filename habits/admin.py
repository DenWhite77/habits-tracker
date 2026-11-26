from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Habit


class CustomUserAdmin(UserAdmin):
    # Добавляем наше поле в отображение формы редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Telegram', {'fields': ('telegram_chat_id',)}),
    )
    # Добавляем поле на страницу создания нового пользователя (опционально)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Telegram', {'fields': ('telegram_chat_id',)}),
    )


admin.site.register(User, CustomUserAdmin)


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'time', 'periodicity', 'is_public')
    list_filter = ('is_public', 'user')
