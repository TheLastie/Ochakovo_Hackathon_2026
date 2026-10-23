"""Content for the standalone career site."""
import json

from django.conf import settings


def load_content():
    return json.loads((settings.BASE_DIR / 'web/content.json').read_text())


def role_choices():
    return [(role['id'], role['title']) for role in load_content()['roles']]


def application_role_choices():
    return role_choices() + [('undecided', 'Пока присматриваюсь')]
