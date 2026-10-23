import uuid

from django.test import Client, TestCase

from .models import Application, OutboxMessage


class ApplicationTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.get('/')
        self.token = self.client.cookies['csrftoken'].value
        self.payload = {
            'idempotency_key': str(uuid.uuid4()),
            'name': 'Тест',
            'email': 'test@example.com',
            'role': 'brewer',
            'consent': True,
        }

    def post(self, payload=None, csrf=True):
        headers = {'HTTP_X_CSRFTOKEN': self.token} if csrf else {}
        return self.client.post(
            '/api/v1/applications/',
            payload or self.payload,
            content_type='application/json',
            **headers,
        )

    def test_submission_is_saved_once(self):
        first = self.post()
        second = self.post()
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json()['id'], second.json()['id'])
        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(OutboxMessage.objects.count(), 1)

    def test_csrf_is_required(self):
        self.assertEqual(self.post(csrf=False).status_code, 403)

    def test_consent_and_role_are_validated(self):
        self.assertEqual(self.post({**self.payload, 'consent': False}).status_code, 400)
        self.assertEqual(self.post({**self.payload, 'role': 'invalid'}).status_code, 400)
        self.assertEqual(Application.objects.count(), 0)

    def test_idempotency_key_cannot_change_payload(self):
        self.post()
        self.assertEqual(self.post({**self.payload, 'name': 'Другой'}).status_code, 409)

    def test_second_browser_cannot_reuse_submission_key(self):
        self.post()
        self.client = Client(enforce_csrf_checks=True)
        self.client.get('/')
        self.token = self.client.cookies['csrftoken'].value
        self.assertEqual(self.post().status_code, 409)

    def test_admin_requires_login(self):
        self.assertEqual(self.client.get('/admin102/career/application/').status_code, 302)
