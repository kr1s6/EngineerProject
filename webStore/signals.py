from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from threading import Thread
import time
from .models import Order

# Signal to change delivery status
@receiver(post_save, sender=Order)
def simulate_status_update(sender, instance, created, **kwargs):
    if created:
        status_flow = ['created', 'processing', 'in_delivery', 'ready_for_pickup', 'completed']
        def update_status(order, statuses):
            for status in statuses:
                time.sleep(10)
                order.status = status
                order.save()

        # Run update function in background
        from threading import Thread
        Thread(target=update_status, args=(instance, status_flow[1:])).start()