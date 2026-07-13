"""
Migration 0002 — Add care_service FK to Booking and make service_package nullable.

Rationale:
  CareService is the display model (ServicesPage / ServiceDetailPage).
  ServicePackage is the legacy booking model.
  We bridge them by adding a nullable care_service FK so the booking creation
  flow can accept a care_service_id directly from the UI.
"""

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0001_initial"),
        ("services", "0002_servicecategory_careservice"),
    ]

    operations = [
        # 1. Make service_package nullable so CareService-only bookings are valid
        migrations.AlterField(
            model_name="booking",
            name="service_package",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bookings",
                to="services.servicepackage",
            ),
        ),
        # 2. Add care_service FK (nullable — backward compatible with old bookings)
        migrations.AddField(
            model_name="booking",
            name="care_service",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bookings",
                to="services.careservice",
            ),
        ),
        # 3. Add service_name snapshot so we never lose display info
        migrations.AddField(
            model_name="booking",
            name="service_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
