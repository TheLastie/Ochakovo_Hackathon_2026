from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('career', '0005_alter_application_role'),
    ]

    operations = [
        migrations.DeleteModel(name='Event'),
    ]
