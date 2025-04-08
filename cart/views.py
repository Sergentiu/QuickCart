from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .cart import Cart
from django.conf import settings
import stripe
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Order, OrderItem
from shop.models import Product
from django.contrib import messages
from .forms import AddToCartForm
from shop.behavior_tracker import BehaviorTracker

stripe.api_key = settings.STRIPE_SECRET_KEY  # Set Stripe API key

@login_required
def cart_view(request):
    cart = Cart(request)
    total_price = cart.get_total_price  # Calculate total price of the cart
    return render(request, "cart.html", {"cart": cart, "total_price": total_price})

@login_required
@require_POST
def add_to_cart_view(request, productid):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 0))  # Get the quantity from POST data
    cart.add(productid, quantity)  # Add product to the cart
    return redirect("cart_url")

@login_required
@require_POST
def empty_cart_view(request):
    request.session['cart'] = {}  # Empty the cart in session
    return redirect("cart_url")

@login_required
def checkout_view(request):
    cart = Cart(request)
    total_price = cart.get_total_price
    
    if request.method == 'POST':
        token = request.POST.get('stripeToken')  # Get Stripe token from POST data
        try:
            # Create the order first with pending status
            order = Order.objects.create(
                user=request.user,
                total=total_price,
                status='pending'  # Start with pending status
            )

            # Create OrderItem entries for each product in the cart
            for item in cart.get_items():
                product_id = item['product_id']
                quantity = item['quantity']
                
                try:
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price  # Store the current price of the product
                    )
                except Product.DoesNotExist:
                    continue  # Skip if the product no longer exists
            
            # Process payment with Stripe
            charge = stripe.Charge.create(
                amount=int(total_price * 100),  # Stripe accepts amounts in cents
                currency='usd',
                description=f'Order {order.id} by {request.user.username}',
                source=token
            )
            
            # If payment successful, update order status to completed
            order.status = 'completed'
            order.save()
            
            # Empty the cart after successful payment
            request.session['cart'] = {}
            return redirect('payment_success')
        
        except stripe.error.StripeError as e:
            # If payment fails, update order status to canceled
            if 'order' in locals():  # Check if order was created
                order.status = 'canceled'
                order.save()
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'checkout.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'total_price': total_price
    })

@login_required
def payment_success(request):
    return render(request, 'payment_success.html')  # Render success page after payment

@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = AddToCartForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            update_quantity=cd['update']
        )
        
        # Track cart addition
        BehaviorTracker.track_behavior(
            user=request.user,
            product=product,
            interaction_type='cart_add',
            metadata={
                'quantity': cd['quantity'],
                'update': cd['update']
            }
        )
        
        messages.success(request, 'Product added to cart successfully')
    return redirect('cart:cart_detail')

@login_required
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Track cart removal
    BehaviorTracker.track_behavior(
        user=request.user,
        product=product,
        interaction_type='cart_remove'
    )
    
    cart.remove(product)
    messages.success(request, 'Product removed from cart successfully')
    return redirect('cart:cart_detail')

@login_required
def clear_cart(request):
    cart = Cart(request)
    
    # Track cart clearing
    for item in cart:
        BehaviorTracker.track_behavior(
            user=request.user,
            product=item['product'],
            interaction_type='cart_remove',
            metadata={'cleared_cart': True}
        )
    
    cart.clear()
    messages.success(request, 'Cart cleared successfully')
    return redirect('cart:cart_detail')