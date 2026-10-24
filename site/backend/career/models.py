import uuid

from django.db import models

from .content import application_role_choices


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idempotency_key = models.UUIDField(unique=True)
    session_key = models.CharField(max_length=64)
    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    role = models.CharField(max_length=40, choices=application_role_choices)
    availability = models.CharField(
        'Когда удобно начать',
        max_length=200,
        blank=True)
    consent_version = models.CharField(
        max_length=40, default='career-interest-')
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    status = models.CharField(
        max_length=30,
        default='new',
        choices=[('new', 'Новая'), ('contacted', 'Связались'),
                 ('closed', 'Закрыта')],
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'анкета'
        verbose_name_plural = 'анкеты'


class OutboxMessage(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    destination = models.CharField(max_length=40, default='internal_hr')


class Event(models.Model):
    KINDS = [
        ('visit', 'Посещение'),
        ('video_open', 'Открытие видео'),
        ('video_play', 'Воспроизведение видео'),
        ('video_complete', 'Видео досмотрено'),
        ('game_open', 'Открытие игры'),
        ('role_selected', 'Выбор профессии'),
        ('game_start', 'Начало смены'),
        ('game_complete', 'Завершение смены'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=64, db_index=True)
    kind = models.CharField(max_length=30, choices=KINDS, db_index=True)
    role = models.CharField(max_length=40, blank=True)
    video = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'событие'
        verbose_name_plural = 'события'
