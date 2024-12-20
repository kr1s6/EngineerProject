from .models import Order

def last_order(request):
    """
    Dodaje ostatnie zamówienie użytkownika do kontekstu szablonów.
    """
    if request.user.is_authenticated:
        return {
            'order': Order.objects.filter(user=request.user).last()
        }
    return {}