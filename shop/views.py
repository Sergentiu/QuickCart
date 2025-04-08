from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Category, FAQ, Policy
from cart.forms import AddToCartForm
from rest_framework import generics
from .serializers import ProductSerializer
from .recommender import get_hybrid_recommendations
from .behavior_tracker import BehaviorTracker

@login_required
def product_list_view(request):
    category_slug = request.GET.get('category')
    products = Product.objects.all()
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    categories = Category.objects.all()
    
    # Track product views if user is authenticated
    if request.user.is_authenticated:
        # Track views for displayed products
        for product in products:
            BehaviorTracker.track_behavior(
                user=request.user,
                product=product,
                interaction_type='view',
                metadata={'from_list': True}
            )
    
    # Get user interests if user is authenticated
    user_interests = None
    if request.user.is_authenticated:
        user_interests = BehaviorTracker.get_user_interests(request.user)
    
    context = {
        'products': products,
        'categories': categories,
        'user_interests': user_interests,
        'dark_mode': request.session.get('dark_mode', False),
        'current_category': category_slug
    }
    
    return render(request, 'product_list.html', context)

@login_required
def product_details_view(request, slug):
    product = Product.objects.filter(slug=slug).first()
    if not product:
        return render(request, "404.html", status=404)

    # Track product view
    if request.user.is_authenticated:
        BehaviorTracker.track_behavior(
            user=request.user,
            product=product,
            interaction_type='view'
        )

    add_to_cart_form = AddToCartForm()
    
    # Get hybrid recommendations
    recommended_products = []
    recent_interests = {}
    behavior_based_products = []
    popular_products = []

    if request.user.is_authenticated:
        # Get hybrid recommendations
        recommended_names = get_hybrid_recommendations(
            user_id=request.user.id,
            product_name=product.name,
            num_recommendations=5
        )
        recommended_products = Product.objects.filter(name__in=recommended_names, available=True)

        # Get recent user interests (last 7 days)
        recent_interests = BehaviorTracker.get_user_interests(request.user, days=7)
        
        # Get behavior-based recommendations
        behavior_products = set()
        for category, score in sorted(recent_interests.items(), key=lambda x: x[1], reverse=True)[:3]:
            # Get products from each of the top 3 categories of interest
            category_products = Product.objects.filter(
                category__name=category, 
                available=True
            ).exclude(id=product.id)[:2]
            behavior_products.update(category_products)
        behavior_based_products = list(behavior_products)

        # Get popular products from user's interested categories
        user_interests = BehaviorTracker.get_user_interests(request.user)
        for category in sorted(user_interests.items(), key=lambda x: x[1], reverse=True)[:2]:
            popular_products.extend(BehaviorTracker.get_popular_products(category=category[0], days=30)[:3])

    context = {
        'product': product,
        'add_form': add_to_cart_form,
        'recommended_products': recommended_products,
        'popular_products': popular_products,
        'recent_interests': recent_interests,
        'behavior_based_products': behavior_based_products,
        'dark_mode': request.session.get('dark_mode', False),
    }
    return render(request, "product_details.html", context)

@login_required
def category_details_view(request, slug):
    category = Category.objects.filter(slug=slug).first()
    products = Product.objects.filter(category=category)
    
    # Track category view
    for product in products:
        BehaviorTracker.track_behavior(
            user=request.user,
            product=product,
            interaction_type='view',
            metadata={'category_view': True}
        )
    
    context = {
        'category': category,
        'products': products,
        'dark_mode': request.session.get('dark_mode', False),
    }
    return render(request, "category_details.html", context)

def faq_page(request):
    faqs = FAQ.objects.all()
    return render(request, 'faq_page.html', {
        'faqs': faqs,
        'dark_mode': request.session.get('dark_mode', False),
    })

def policies_page(request):
    policies = Policy.objects.all()
    return render(request, 'policies_page.html', {
        'policies': policies,
        'dark_mode': request.session.get('dark_mode', False),
    })

def toggle_dark_mode(request):
    if request.method == "POST":
        dark_mode = request.session.get('dark_mode', False)
        request.session['dark_mode'] = not dark_mode
        request.session.modified = True  
        return JsonResponse({'dark_mode': request.session['dark_mode']})
    return JsonResponse({'dark_mode': request.session.get('dark_mode', False)})

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer