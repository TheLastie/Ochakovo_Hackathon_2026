from django.contrib import admin

from .models import Application


class CareerAdminSite(admin.AdminSite):
    site_header = 'Очаково · команда'
    site_title = 'Очаково — анкеты'
    index_title = 'Анкеты кандидатов'


site = CareerAdminSite(name='career_admin')


@admin.register(Application, site=site)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'status', 'created_at')
    list_filter = ('status', 'role', 'created_at')
    readonly_fields = (
        'id', 'created_at', 'consent_version', 'idempotency_key', 'session_key'
    )
    search_fields = ('name', 'email')
    list_editable = ('status',)
    fieldsets = (
        (None, {'fields': ('name', 'email', 'role', 'availability', 'status', 'created_at')}),
        ('Служебные данные', {
            'fields': ('id', 'consent_version', 'idempotency_key', 'session_key'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        return False
