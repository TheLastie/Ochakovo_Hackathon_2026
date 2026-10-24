from .content import load_content
from tempfile import TemporaryDirectory
from .models import Event
from django.contrib.auth import get_user_model
import json
from django.test import override_settings
from pathlib import Path
import uuid
from django.test import TestCase, Client
from .models import Application, OutboxMessage


class ApplicationTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.get('/')
        self.token = self.client.cookies['csrftoken'].value
        self.payload = {
            'idempotency_key': str(
                uuid.uuid4()),
            'name': 'Тест',
            'email': 'test@example.com',
            'role': 'brewer',
            'consent': True}

    def post(self, payload=None, csrf=True):
        return self.client.post('/api/v1/applications/', payload or self.payload,
                                content_type='application/json', **({'HTTP_X_CSRFTOKEN': self.token} if csrf else {}))

    def test_saved_atomically_and_duplicate_returns_same_id(self):
        first = self.post()
        second = self.post()
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json()['id'], second.json()['id'])
        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(OutboxMessage.objects.count(), 1)

    def test_csrf_required(self): self.assertEqual(
        self.post(csrf=False).status_code, 403)

    def test_consent_and_role_validated(self):
        self.assertEqual(
            self.post({**self.payload, 'consent': False}).status_code, 400)
        self.assertEqual(
            self.post({**self.payload, 'role': 'invalid'}).status_code, 400)
        self.assertEqual(Application.objects.count(), 0)

    def test_key_cannot_change_payload(self):
        self.post()
        self.assertEqual(
            self.post({**self.payload, 'name': 'Другой'}).status_code, 409)

    def test_other_browser_cannot_access_existing_record(self):
        self.post()
        self.client = Client(enforce_csrf_checks=True)
        self.client.get('/')
        self.token = self.client.cookies['csrftoken'].value
        self.assertEqual(self.post().status_code, 409)

    def test_hr_requires_login(self): self.assertEqual(
        self.client.get('/admin102/career/application/').status_code, 302)


class AnalyticsTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.get('/')
        self.token = self.client.cookies['csrftoken'].value

    def event(self, payload, csrf=True):
        return self.client.post('/api/v1/events/', payload, content_type='application/json',
                                **({'HTTP_X_CSRFTOKEN': self.token} if csrf else {}))

    def test_pageviews_and_anonymous_browser_identity(self):
        self.client.get('/')
        other = Client()
        other.get('/')
        visits = Event.objects.filter(kind='visit')
        self.assertEqual(visits.count(), 3)
        self.assertEqual(visits.values('session_key').distinct().count(), 2)
        self.assertNotEqual(
            visits.first().session_key,
            self.client.session.session_key)

    def test_event_dedup_and_validation(self):
        payload = {
            'id': str(
                uuid.uuid4()),
            'kind': 'game_start',
            'role': 'chemist'}
        self.assertEqual(self.event(payload).status_code, 201)
        self.assertEqual(self.event(payload).status_code, 200)
        self.assertEqual(Event.objects.filter(kind='game_start').count(), 1)
        self.assertEqual(self.event(
            {**payload, 'role': 'brewer'}).status_code, 409)
        self.assertEqual(self.event(
            {'id': str(uuid.uuid4()), 'kind': 'game_start'}).status_code, 400)
        self.assertEqual(self.event(
            {'id': str(uuid.uuid4()), 'kind': 'visit'}).status_code, 400)
        self.assertEqual(self.event(payload, csrf=False).status_code, 403)

    def test_placeholder_is_not_video_playback(self):
        self.event({'id': str(uuid.uuid4()),
                   'kind': 'video_open', 'video': 'brand'})
        self.assertEqual(Event.objects.filter(kind='video_open').count(), 1)
        self.assertEqual(Event.objects.filter(kind='video_play').count(), 0)

    def test_dashboard_requires_superuser_and_aggregates(self):
        self.assertEqual(self.client.get('/admin102/').status_code, 302)
        self.assertEqual(self.client.get('/admin/').status_code, 404)
        user = get_user_model().objects.create_user(
            username='reader', password='test-password')
        self.client.force_login(user)
        self.assertEqual(self.client.get('/admin102/').status_code, 302)
        user.is_staff = True
        user.save()
        self.assertEqual(self.client.get('/admin102/').status_code, 302)
        user.is_superuser = True
        user.save()
        self.event({'id': str(uuid.uuid4()),
                   'kind': 'game_start', 'role': 'chemist'})
        result = self.client.get('/admin102/?period=all')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.context['popularity'][0]['title'], 'Химик-лаборант')
        self.assertEqual(result.context['popularity'][0]['total'], 1)


class ContentTests(TestCase):
    def test_videos_are_discovered_without_editing_json(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'web/public/videos').mkdir(parents=True)
            (root / 'company-videos').mkdir()
            original = {'brandVideo': {'src': '', 'captions': '', 'title': 'Test', 'transcript': ''}, 'roles': [
                {'id': 'brewer', 'title': 'Квасовар', 'video': {'src': '', 'captions': ''}}]}
            (root / 'web/content.json').write_text(json.dumps(original))
            with override_settings(BASE_DIR=root, COMPANY_VIDEO_DIR=root / 'company-videos'):
                self.assertEqual(
                    load_content()['roles'][0]['video']['src'], '')
                (root / 'web/public/videos/brewer.webm').touch()
                self.assertTrue(load_content()['roles'][0]['video']['src'].startswith(
                    '/static/videos/brewer.webm?v='))
                (root / 'web/public/videos/brewer.mp4').touch()
                (root / 'web/public/videos/brewer.ru.vtt').touch()
                (root / 'company-videos/brand.mp4').touch()
                data = load_content()
                self.assertTrue(data['roles'][0]['video']['src'].startswith(
                    '/static/videos/brewer.mp4?v='))
                self.assertTrue(data['roles'][0]['video']['captions'].startswith(
                    '/static/videos/brewer.ru.vtt?v='))
                previous = data['roles'][0]['video']['src']
                import os
                file = root / 'web/public/videos/brewer.mp4'
                stamp = file.stat().st_mtime_ns + 1000000
                os.utime(file, ns=(stamp, stamp))
                self.assertNotEqual(
                    load_content()['roles'][0]['video']['src'], previous)
                self.assertTrue(data['brandVideo']['src'].startswith(
                    '/static/videos/brand.mp4?v='))
                (root / 'web/public/videos/brewer.mp4').unlink()
                self.assertTrue(load_content()['roles'][0]['video']['src'].startswith(
                    '/static/videos/brewer.webm?v='))


@override_settings(ALLOWED_HOSTS=['career.example.test'],
                   CSRF_TRUSTED_ORIGINS=['https://career.example.test'],
                   SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'),
                   CSRF_COOKIE_SECURE=True, SESSION_COOKIE_SECURE=True)
class PublicProxyTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.headers = {
            'HTTP_HOST': 'career.example.test',
            'HTTP_X_FORWARDED_PROTO': 'https'}
        self.page = self.client.get('/', **self.headers)
        self.payload = {'idempotency_key': str(uuid.uuid4()), 'name': 'Proxy test',
                        'email': 'proxy@example.test', 'role': 'chemist', 'consent': True}

    def submit(self, origin):
        return self.client.post('/api/v1/applications/', self.payload,
                                content_type='application/json',
                                HTTP_ORIGIN=origin,
                                HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value,
                                **self.headers)

    def test_https_proxy_preserves_csrf_and_secure_cookies(self):
        self.assertTrue(self.page.wsgi_request.is_secure())
        self.assertTrue(self.page.cookies['csrftoken']['secure'])
        self.assertTrue(self.page.cookies['sessionid']['secure'])
        self.assertEqual(
            self.submit('https://career.example.test').status_code, 201)
        self.assertEqual(OutboxMessage.objects.count(), 1)

    def test_foreign_origin_cannot_submit_even_with_token(self):
        self.assertEqual(
            self.submit('https://untrusted.example.test').status_code, 403)
        self.assertEqual(Application.objects.count(), 0)


class EditableCatalogTests(TestCase):
    def test_catalog_changes_apply_without_restarting_django(self):
        from .views import ApplicationSerializer, EventSerializer
        from .content import application_role_choices
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'web/public/videos').mkdir(parents=True)
            data = {'brandVideo': {'src': '', 'captions': ''}, 'roles': [{'id': 'lab_assistant', 'title': 'Лаборант'}],
                    'retiredRoles': [{'id': 'chemist', 'title': 'Химик-лаборант'}]}
            path = root / 'web/content.json'
            path.write_text(json.dumps(data))
            payload = {
                'idempotency_key': str(
                    uuid.uuid4()),
                'name': 'Catalog test',
                'email': 'catalog@example.com',
                'role': 'lab_assistant',
                'consent': True}
            with override_settings(BASE_DIR=root):
                self.assertTrue(ApplicationSerializer(data=payload).is_valid())
                self.assertFalse(
                    ApplicationSerializer(
                        data={
                            **payload,
                            'role': 'mikh'}).is_valid())
                event = EventSerializer(
                    data={
                        'id': str(
                            uuid.uuid4()),
                        'kind': 'game_complete',
                        'role': 'mikh'})
                self.assertFalse(event.is_valid())
                self.assertIn(('chemist', 'Химик-лаборант'), application_role_choices())
                data['roles'] = [{'id': 'warehouse', 'title': 'Кладовщик'}]
                path.write_text(json.dumps(data))
                self.assertFalse(
                    ApplicationSerializer(
                        data=payload).is_valid())
                self.assertTrue(
                    ApplicationSerializer(
                        data={
                            **payload,
                            'role': 'warehouse'}).is_valid())
                (root / 'web/public/videos/lab_assistant.mp4').touch()
                self.assertIn(
                    '/lab_assistant.mp4?',
                    load_content()['roles'][0]['video']['src'])
