from django.db.models.signals import post_save
from django.dispatch import receiver
from threading import Thread
import time
from .models import Order, Message

@receiver(post_save, sender=Order)
def simulate_status_update(sender, instance, created, **kwargs):
    if created:
        status_flow = ['processing', 'in_delivery', 'ready_for_pickup', 'completed']

        def update_status(order, statuses):
            for status in statuses:
                time.sleep(4)
                order.status = status
                order.save(update_fields=['status'])

        Thread(target=update_status, args=(instance, status_flow)).start()

@receiver(post_save, sender=Order)
def handle_status_update(sender, instance, **kwargs):
    """Tworzy wiadomość do użytkownika po aktualizacji statusu zamówienia."""
    if not kwargs.get('created'):  # Jeśli zamówienie zostało zaktualizowane
        content = f"""
        Witaj {instance.user.first_name},

        Status Twojego zamówienia #{instance.id} został zaktualizowany.
        Obecny status: {instance.get_status_display()}.

        Dziękujemy za zakupy w naszym sklepie!
        """

        Message.objects.create(
            sender=None,  # Możesz ustawić None lub np. "System"
            recipient=instance.user,
            content=content.strip()
        )