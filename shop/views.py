from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Category, FAQ, Policy
from cart.forms import AddToCartForm
from rest_framework import generics
from .serializers import ProductSerializer
from .recommender import get_product_recommendations, get_collaborative_recommendations

@login_required
def product_list_view(request):
    products = Product.objects.all()
    context = {
        'products': products,
        'dark_mode': request.session.get('dark_mode', False),
    }
    return render(request, "product_list.html", context)

@login_required
def product_details_view(request, slug):
    product = Product.objects.filter(slug=slug).first()
    if not product:
        return render(request, "404.html", status=404)

    add_to_cart_form = AddToCartForm()
    # Content-based recommendations
    content_recommendations = get_product_recommendations(product.name, num_recommendations=5)
    content_recommended_products = Product.objects.filter(name__in=content_recommendations, available=True)
    
    # Collaborative recommendations (based on user purchase history)
    collab_recommendations = get_collaborative_recommendations(request.user.id, num_recommendations=5)
    collab_recommended_products = Product.objects.filter(name__in=collab_recommendations, available=True)

    context = {
        'product': product,
        'add_form': add_to_cart_form,
        'content_recommended_products': content_recommended_products,
        'collab_recommended_products': collab_recommended_products,
        'dark_mode': request.session.get('dark_mode', False),
    }
    return render(request, "product_details.html", context)

@login_required
def category_details_view(request, slug):
    category = Category.objects.filter(slug=slug).first()
    products = Product.objects.filter(category=category)
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