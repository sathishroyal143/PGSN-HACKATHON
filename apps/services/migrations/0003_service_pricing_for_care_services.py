from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_servicecategory_careservice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicepricing',
            name='package',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='pricing',
                to='services.servicepackage',
            ),
        ),
        migrations.AddField(
            model_name='servicepricing',
            name='service',
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='pricing_history',
                to='services.careservice',
            ),
        ),
        migrations.AddField(
            model_name='servicepricing',
            name='emergency_charge',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                help_text='Flat emergency charge in INR',
                max_digits=10,
            ),
        ),
        migrations.AddField(
            model_name='servicepricing',
            name='instant_charge',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                help_text='Flat instant booking charge in INR',
                max_digits=10,
            ),
        ),
        migrations.AddField(
            model_name='servicepricing',
            name='tax',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                help_text='Flat tax amount in INR',
                max_digits=10,
            ),
        ),
        migrations.AddField(
            model_name='servicepricing',
            name='discount',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                help_text='Flat discount amount in INR',
                max_digits=10,
            ),
        ),
        migrations.AddField(
            model_name='servicepricing',
            name='total_price',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                help_text='Computed final service price in INR',
                max_digits=10,
            ),
        ),
        migrations.AddField(
            model_name='servicepricing',
            name='effective_to',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='servicepricing',
            index=models.Index(
                fields=['service', 'is_active', 'effective_from'],
                name='service_pri_service_175329_idx',
            ),
        ),
    ]
