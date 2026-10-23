import uuid

from django.db import models

from .content import application_role_choices


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idempotency_key = models.UUIDField(unique=True)
    session_key = models.CharField(max_length=64)
    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    role = models.CharField(
        'Направление', max_length=40, choices=application_role_choices
    )
    availability = models.CharField('Когда удобно начать', max_length=200, blank=True)
    consent_version = models.CharField(max_length=40, default='career-interest-')
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    status = models.CharField(
        'Статус',
        max_length=30,
        default='new',
        choices=[('new', 'Новая'), ('contacted', 'Связались'), ('closed', 'Закрыта')],
    )

    class Meta:
        verbose_name = 'анкета'
        verbose_name_plural = 'анкеты'

    def __str__(self):
        return self.name


class OutboxMessage(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    destination = models.CharField(max_length=40, default='internal_hr')
