from django.db import migrations


def seed_default_catalog(apps, schema_editor):
    from apps.services.catalog import seed_default_service_catalog

    seed_default_service_catalog()


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_service_pricing_for_care_services'),
    ]

    operations = [
        migrations.RunPython(seed_default_catalog, migrations.RunPython.noop),
    ]
