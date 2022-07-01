from django.contrib import admin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass


empty_value_display = '-пусто-'
