from django.urls import path
from .views import *

urlpatterns = [
    # Shop and Product Views
    path("", product_list_view, name="shop_url"),
    path("category/<slug>", category_details_view, name="category_details"),
    path("<slug>", product_details_view, name="product_details"),

    # API Endpoints
    path("api/products", ProductListView.as_view(), name="api_products"),
    path("api/products/details/<pk>", ProductDetailView.as_view(), name="api_product_details"),
    path("api/products/create", ProductCreateView.as_view(), name="api_product_create"),

    # FAQ and Policies
    path("faq/", faq_page, name="faq_page"),
    path("policies/", policies_page, name="policies_page"),

    # Dark Mode Toggle
    path("toggle-dark-mode/", toggle_dark_mode, name="toggle_dark_mode"),
]