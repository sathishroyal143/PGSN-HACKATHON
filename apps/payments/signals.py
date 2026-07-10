"""Payments signals — auto-generate invoice when booking is completed."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger('carebridge')


@receiver(post_save, sender='bookings.Booking')
def auto_generate_invoice(sender, instance, created, **kwargs):
    if instance.status != 'completed':
        return
    from apps.payments.models import Invoice
    if Invoice.objects.filter(booking=instance).exists():
        return
    try:
        from apps.payments.services import InvoiceService
        InvoiceService.generate(
            booking_id=instance.id,
            user_id=instance.family_user_id,
            subtotal=float(instance.final_price or instance.quoted_price),
            line_items=[{'description': str(instance.service_package), 'amount': float(instance.quoted_price)}],
        )
    except Exception as exc:
        logger.error("Failed to auto-generate invoice for booking %s: %s", instance.id, exc)
