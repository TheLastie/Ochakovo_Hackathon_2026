from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from career.models import OutboxMessage
class Command(BaseCommand):
 help='Mark records available in the internal HR inbox; no external delivery.'
 def handle(self,*args,**options):
 with transaction.atomic():
 rows=OutboxMessage.objects.select_for_update().filter(delivered_at__isnull=True,destination='internal_hr')[:100]
 count=0
 for row in rows:
 row.delivered_at=timezone.now();row.save(update_fields=['delivered_at']);count+=1
 self.stdout.write(f'Internal HR inbox: {count} records acknowledged')
