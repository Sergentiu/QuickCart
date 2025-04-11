from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap as sitemap_view
from shop.sitemaps import ProductSitemap, CategorySitemap

# Import the two-factor URL tuple and the two-factor login view
from two_factor import urls as two_factor_urls
from two_factor.views import LoginView as TwoFactorLoginView

# Import the custom registration view
from profileapp.views import CustomActivationRegistrationView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls')),
    path('shop/', include('shop.urls')),
    path('', include('homepage.urls')),

    # Override the registration view to use our custom form
    path('accounts/register/', CustomActivationRegistrationView.as_view(), name='django_registration_register'),

    # Continue to use the rest of django-registration (activation flow)
    path('accounts/', include('django_registration.backends.activation.urls')),

    # 1) Override the default login with the two-factor login view.
    path('accounts/login/', TwoFactorLoginView.as_view(), name='login'),

    # 2) Keep the rest of the auth routes (logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Profile app
    path('accounts/', include('profileapp.urls')),

    # Sitemap
    path('sitemap.xml/', sitemap_view, {
        'sitemaps': {
            'products': ProductSitemap(),
            'categories': CategorySitemap()
        }
    }),

    # Two-factor setup/disable/backup routes
    path(
        'account/2fa/',
        include(
            (
                two_factor_urls.urlpatterns[0],
                two_factor_urls.urlpatterns[1]
            ),
            namespace='two_factor'
        )
    ),

    # Chatbot
    path('chatbot/', include('chatbot.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)