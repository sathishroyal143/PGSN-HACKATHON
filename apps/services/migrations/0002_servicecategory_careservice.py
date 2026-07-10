# Generated migration for ServiceCategory and CareService models

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(
                    choices=[
                        ('SCHEDULED_CARE', 'Scheduled Care'),
                        ('INSTANT_CARE', 'Instant Care'),
                        ('EMERGENCY_CARE', 'Emergency Care'),
                    ],
                    db_index=True,
                    max_length=30,
                    unique=True,
                )),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Service Category',
                'verbose_name_plural': 'Service Categories',
                'db_table': 'service_categories',
                'ordering': ['name'],
            },
        ),
        migrations.AddIndex(
            model_name='servicecategory',
            index=models.Index(fields=['code', 'is_active'], name='service_cat_code_is_active_idx'),
        ),
        migrations.CreateModel(
            name='CareService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('service_name', models.CharField(max_length=200, unique=True)),
                ('service_code', models.CharField(db_index=True, max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('estimated_duration', models.PositiveIntegerField(
                    help_text='Estimated service duration in minutes',
                )),
                ('base_price', models.DecimalField(
                    decimal_places=2,
                    help_text='Base price in INR',
                    max_digits=10,
                )),
                ('home_visit_supported', models.BooleanField(db_index=True, default=False)),
                ('hospital_visit_supported', models.BooleanField(db_index=True, default=False)),
                ('emergency_supported', models.BooleanField(db_index=True, default=False)),
                ('ai_recommended', models.BooleanField(
                    db_index=True,
                    default=False,
                    help_text='Surfaced by AI matching engine',
                )),
                ('icon', models.CharField(blank=True, help_text='Icon class or URL', max_length=100)),
                ('status', models.CharField(
                    choices=[
                        ('ACTIVE', 'Active'),
                        ('INACTIVE', 'Inactive'),
                        ('DRAFT', 'Draft'),
                    ],
                    db_index=True,
                    default='ACTIVE',
                    max_length=10,
                )),
                ('is_deleted', models.BooleanField(db_index=True, default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('service_category', models.ForeignKey(
                    db_index=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='care_services',
                    to='services.servicecategory',
                )),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_care_services',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('updated_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='updated_care_services',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Care Service',
                'verbose_name_plural': 'Care Services',
                'db_table': 'care_services',
                'ordering': ['service_name'],
            },
        ),
        migrations.AddIndex(
            model_name='careservice',
            index=models.Index(
                fields=['service_category', 'status', 'is_deleted'],
                name='care_svc_cat_stat_del_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='careservice',
            index=models.Index(fields=['service_code'], name='care_svc_code_idx'),
        ),
        migrations.AddIndex(
            model_name='careservice',
            index=models.Index(
                fields=['emergency_supported', 'status'],
                name='care_svc_emergency_status_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='careservice',
            index=models.Index(
                fields=['ai_recommended', 'status'],
                name='care_svc_ai_status_idx',
            ),
        ),
    ]
