from django.conf import settings
from django.db import transaction
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .content import application_role_choices, load_content
from .models import Application, OutboxMessage


@ensure_csrf_cookie
def index(request):
    assets = [settings.BASE_DIR / 'web/dist' / name for name in ('app.js', 'app.css')]
    asset_version = max(
        (path.stat().st_mtime_ns for path in assets if path.exists()),
        default=0,
    )
    return render(
        request,
        'index.html',
        {'roles': load_content()['roles'], 'asset_version': asset_version},
    )


class ApplicationSerializer(serializers.Serializer):
    idempotency_key = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=254)
    role = serializers.ChoiceField(choices=[key for key, _ in application_role_choices()])
    availability = serializers.CharField(max_length=200, required=False, allow_blank=True)
    consent = serializers.BooleanField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [key for key, _ in application_role_choices()]

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError('Подтвердите согласие на обработку данных.')
        return value


@method_decorator(csrf_protect, name='dispatch')
class Applications(APIView):
    def post(self, request):
        serializer = ApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        data.pop('consent')
        if not request.session.session_key:
            request.session.create()
        key = data.pop('idempotency_key')
        with transaction.atomic():
            application, created = Application.objects.get_or_create(
                idempotency_key=key,
                defaults={**data, 'session_key': request.session.session_key},
            )
            if application.session_key != request.session.session_key:
                return Response(
                    {'detail': 'Ключ уже использован. Обновите страницу.'},
                    status=409,
                )
            if not created and any(
                getattr(application, field) != value
                for field, value in data.items()
            ):
                return Response(
                    {'detail': 'Данные повторной отправки отличаются. Обновите страницу.'},
                    status=409,
                )
            if created:
                OutboxMessage.objects.create(application=application)
        return Response(
            {
                'id': str(application.id),
                'message': 'Спасибо! Анкета сохранена.',
            },
            status=201 if created else 200,
        )
