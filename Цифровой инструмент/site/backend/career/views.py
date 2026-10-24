from django.conf import settings
from django.db import transaction
from django.shortcuts import render
from django.utils.crypto import salted_hmac
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .content import load_content, role_choices
from .models import Application, Event, OutboxMessage


def analytics_session(request):
    if not request.session.session_key:
        request.session.create()
    return salted_hmac('analytics', request.session.session_key,
                       algorithm='sha256').hexdigest()


ROLE_IDS = [key for key, _ in role_choices()]


def content():
    return load_content()


@ensure_csrf_cookie
def index(request):
    if not request.session.session_key:
        request.session.create()
    Event.objects.create(kind='visit', session_key=analytics_session(request))
    assets = [
        settings.BASE_DIR /
        'web/dist' /
        name for name in (
            'app.js',
            'app.css')]
    version = max(
        (path.stat().st_mtime_ns for path in assets if path.exists()),
        default=0)
    page_content = content()
    return render(request, 'index.html', {
                  'content': page_content, 'asset_version': version})


class ApplicationSerializer(serializers.Serializer):
    idempotency_key = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=254)
    role = serializers.ChoiceField(choices=ROLE_IDS + ['undecided'])
    availability = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    consent = serializers.BooleanField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            key for key, _ in role_choices()] + ['undecided']

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError(
                'Подтвердите согласие на обработку данных.')
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
            app, created = Application.objects.get_or_create(
                idempotency_key=key,
                defaults={**data, 'session_key': request.session.session_key},
            )
            if app.session_key != request.session.session_key:
                return Response(
                    {'detail': 'Ключ уже использован. Обновите страницу.'}, status=409)
            if not created and any(getattr(app, field) !=
                                   value for field, value in data.items()):
                return Response(
                    {'detail': 'Данные повторной отправки отличаются. Обновите страницу.'}, status=409)
            if created:
                OutboxMessage.objects.create(application=app)
        return Response(
            {'id': str(app.id), 'message': 'Спасибо! Анкета сохранена.'},
            status=201 if created else 200,
        )


class EventSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    kind = serializers.ChoiceField(
        choices=[
            key for key,
            _ in Event.KINDS if key != 'visit'])
    role = serializers.ChoiceField(
        choices=ROLE_IDS,
        required=False,
        allow_blank=True,
        default='')
    video = serializers.ChoiceField(
        choices=ROLE_IDS +
        ['brand'],
        required=False,
        allow_blank=True,
        default='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = load_content()
        ids = [role['id'] for role in data['roles']]
        self.fields['role'].choices = ids
        self.fields['video'].choices = ids + ['brand']

    def validate(self, data):
        if data['kind'] in ('role_selected', 'game_start',
                            'game_complete') and not data['role']:
            raise serializers.ValidationError('Нужна профессия.')
        if data['kind'].startswith('video_') and not data['video']:
            raise serializers.ValidationError('Нужно видео.')
        return data


class EventThrottle(AnonRateThrottle):
    scope = 'analytics'
    rate = '120/min'


@method_decorator(csrf_protect, name='dispatch')
class Events(APIView):
    throttle_classes = [EventThrottle]

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        event_id = data.pop('id')
        event, created = Event.objects.get_or_create(
            id=event_id,
            defaults={**data, 'session_key': analytics_session(request)},
        )
        if event.session_key != analytics_session(request) or any(
            getattr(event, field) != value for field, value in data.items()
        ):
            return Response({'detail': 'Событие уже существует.'}, status=409)
        return Response({'saved': True}, status=201 if created else 200)
