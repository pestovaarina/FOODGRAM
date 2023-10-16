from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('username',)
    list_filter = ('email', 'username')
    empty_value_display = '-empty-'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'subscriber', 'author')
    search_fields = ('subscriber', 'author')
    list_filter = ('subscriber', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
