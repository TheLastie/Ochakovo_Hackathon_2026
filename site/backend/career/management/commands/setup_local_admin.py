import os
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create a local-only administrator and save a random password in .local-admin.txt (0600).'

    def handle(self, *args, **options):
        if not settings.DEBUG or settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            raise CommandError(
                'Only available in local SQLite development. Use createsuperuser for other environments.')
        User = get_user_model()
        if User.objects.filter(username='localadmin').exists():
            self.stdout.write(
                'localadmin already exists; its password was not changed.')
            return
        target = settings.BASE_DIR / '.local-admin.txt'
        password = secrets.token_urlsafe(24)
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            User.objects.create_superuser(
                username='localadmin', email='', password=password)
            with os.fdopen(fd, 'w') as output:
                output.write(
                    'Local development only\nURL: http://127.0.0.1:8000/admin102/\n'
                    'Login: localadmin\nPassword: ' + password + '\n'
                )
        except Exception:
            target.unlink(missing_ok=True)
            raise
        self.stdout.write(
            'Created localadmin. Credentials saved to .local-admin.txt with owner-only permissions.')
