from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user, is_paid=False)
            return {'cart_count': cart.bookings.count()}
        except Cart.DoesNotExist:
            return {'cart_count': 0}
    return {'cart_count': 0}
