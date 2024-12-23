from django.db.models.signals import post_save
from django.dispatch import receiver
from threading import Thread
import time
from .models import Order

@receiver(post_save, sender=Order)
def simulate_status_update(sender, instance, created, **kwargs):
    if created:
        status_flow = ['processing', 'in_delivery', 'ready_for_pickup', 'completed']

        def update_status(order, statuses):
            for status in statuses:
                time.sleep(10)
                order.status = status
                order.save(update_fields=['status'])

        Thread(target=update_status, args=(instance, status_flow)).start()
