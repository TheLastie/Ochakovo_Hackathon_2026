from datetime import timedelta

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.utils import timezone

from .content import application_role_choices, load_content
from .models import Application, Event


User = get_user_model()


class AdministratorCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CareerAdminSite(admin.AdminSite):
    site_header = 'Очаково · команда'
    site_title = 'Очаково — заявки и статистика'
    index_title = 'Заявки и статистика'
    index_template = 'admin/dashboard.html'

    def has_permission(self, request):
        user = request.user
        return user.is_active and user.is_superuser

    def index(self, request, extra_context=None):
        roles = dict(application_role_choices())
        bonus = load_content().get('bonusRole')
        if bonus:
            roles[bonus['id']] = bonus['title']
        period = request.GET.get('period', '30')
        if period not in ('7', '30', 'all'):
            period = '30'
        events = Event.objects.all()
        applications = Application.objects.all()
        if period != 'all':
            since = timezone.now() - timedelta(days=int(period))
            events = events.filter(created_at__gte=since)
            applications = applications.filter(created_at__gte=since)
        counts = {row['kind']: row['total']
                  for row in events.values('kind').annotate(total=Count('id'))}
        stats = [
            ('Посещения', counts.get('visit', 0)),
            ('Уникальные браузеры', events.filter(kind='visit').values(
                'session_key').distinct().count()),
            ('Открытия видео', counts.get('video_open', 0)),
            ('Запуски видео', counts.get('video_play', 0)),
            ('Досмотры видео', counts.get('video_complete', 0)),
            ('Открытия игры', counts.get('game_open', 0)),
            ('Начатые смены', counts.get('game_start', 0)),
            ('Завершённые смены', counts.get('game_complete', 0)),
            ('Анкеты', applications.count()),
        ]
        popularity = list(
            events.filter(kind='game_start')
            .values('role')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        maximum = max((row['total'] for row in popularity), default=1)
        for row in popularity:
            row.update(
                title=roles.get(
                    row['role'], row['role']), width=round(
                    row['total'] / maximum * 100))
        videos = list(
            events.filter(kind__startswith='video_')
            .values('video', 'kind')
            .annotate(total=Count('id'))
            .order_by('video', 'kind')
        )
        for row in videos:
            row['title'] = 'Знакомство с Михалычем' if row['video'] == 'brand' else roles.get(
                row['video'], row['video'])
            row['action'] = dict(Event.KINDS)[row['kind']]
        context = {
            **(extra_context or {}),
            'stats': stats,
            'popularity': popularity,
            'videos': videos,
            'period': period,
            'recent': applications.order_by('-created_at')[:8],
            'active_admin_count': User.objects.filter(
                is_active=True, is_superuser=True).count(),
        }
        return super().index(request, context)


site = CareerAdminSite(name='career_admin')


@admin.register(User, site=site)
class AdministratorAdmin(UserAdmin):
    add_form = AdministratorCreationForm
    list_display = (
        'username', 'first_name', 'last_name', 'email', 'is_active',
        'last_login')
    list_filter = ('is_active',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = (
        ('Учётная запись', {'fields': ('username', 'password')}),
        ('Сотрудник', {'fields': ('first_name', 'last_name', 'email')}),
        ('Доступ', {'fields': ('is_active',)}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name', 'last_name', 'email',
                'password1', 'password2'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_superuser=True)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change and not obj.is_active:
            another_active_admin = User.objects.filter(
                is_active=True, is_superuser=True).exclude(pk=obj.pk).exists()
            if obj.pk == request.user.pk or not another_active_admin:
                messages.error(
                    request,
                    'Нельзя отключить текущего или последнего активного администратора.')
                obj.is_active = True
        obj.is_staff = True
        obj.is_superuser = True
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        context = {**(extra_context or {}), 'title': 'Учётные записи администраторов'}
        return super().changelist_view(request, context)


@admin.register(Application, site=site)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'status', 'created_at')
    list_filter = ('status', 'role', 'created_at')
    readonly_fields = (
        'id',
        'created_at',
        'consent_version',
        'idempotency_key',
        'session_key')
    search_fields = ('name', 'email')
    list_editable = ('status',)
    fieldsets = (
        (None, {'fields': ('name', 'email', 'role',
         'availability', 'status', 'created_at')}),
        ('Служебные данные',
         {'fields': ('id',
                     'consent_version',
                     'idempotency_key',
                     'session_key'),
          'classes': ('collapse',
                      )}),
    )

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        context = {**(extra_context or {}), 'title': 'Заявки'}
        return super().changelist_view(request, context)
