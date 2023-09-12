from django.contrib import admin
from .models import Code, Setting, Interhub, TypeAccount, Account, Game


@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'link', 'game', 'status', 'date')
    search_fields = ('code',)


@admin.register(Game)
class CodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_id', 'type', "amount")
    search_fields = ('game_id',)


@admin.register(TypeAccount)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('type_name',)


@admin.register(Account)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('login', 'password', 'type', 'status')


@admin.register(Interhub)
class InterhubAdmin(admin.ModelAdmin):
    list_display = ('token', 'balance')


@admin.register(Setting)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'digi_code')
