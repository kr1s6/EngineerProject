from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from threading import Thread
import time
from .models import Order, Message, Conversation

@receiver(post_save, sender=Order)
def simulate_status_update(sender, instance, created, **kwargs):
    """Symulacja zmiany statusu zamówienia w czasie."""
    if created:
        status_flow = ['processing', 'in_delivery', 'ready_for_pickup', 'completed']

        def update_status(order, statuses):
            for status in statuses:
                if order.status == 'completed':
                    break  # Jeśli status już jest "completed", przerywamy
                time.sleep(5)  # Symulacja opóźnienia
                order.status = status
                order.save(update_fields=['status'])

        Thread(target=update_status, args=(instance, status_flow)).start()

@receiver(pre_save, sender=Order)
def track_previous_status(sender, instance, **kwargs):
    """Śledzenie poprzedniego statusu zamówienia przed zapisaniem."""
    if instance.pk:  # Jeśli zamówienie istnieje
        previous_order = Order.objects.filter(pk=instance.pk).first()
        if previous_order:
            instance.previous_status = previous_order.status


@receiver(post_save, sender=Order)
def create_or_update_conversation(sender, instance, created, **kwargs):
    """Tworzenie konwersacji i wiadomości przy tworzeniu zamówienia lub zmianie statusu."""
    if created:
        conversation = Conversation.objects.create(order=instance)
        conversation.participants.add(instance.user)

        Message.objects.create(
            conversation=conversation,
            sender=None,  # Wiadomość systemowa
            content=f"Twoje zamówienie zostało utworzone. Obecny status: {instance.get_status_display()}."
        )
    else:
        # Obsługa zmiany statusu zamówienia
        if instance.previous_status != instance.status:  # Jeśli status się zmienił
            Message.objects.create(
                conversation=instance.conversation,
                sender=None,
                content=f"Status Twojego zamówienia zmienił się z {instance.get_status_display()} na {instance.get_status_display()}."
            )


