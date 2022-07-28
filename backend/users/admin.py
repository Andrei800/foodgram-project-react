from django.contrib import admin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'email',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('username', 'email',)


empty_value_display = "-пусто-"
