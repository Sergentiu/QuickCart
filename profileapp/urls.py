# from django.urls import path
# from .views import profile_view, register_view, change_username, change_email, change_password

# urlpatterns = [
#     path('profile/', profile_view, name="profile_url"),
#     path('register/', register_view, name='register_url'),
#     path('change-username/', change_username, name='change_username'),
#     path('change-email/', change_email, name='change_email'),
#     path('change-password/', change_password, name='change_password'),
# ]

from django.urls import path
from .views import profile_view, change_username, change_email, change_password

urlpatterns = [
    path('profile/', profile_view, name="profile_url"),
    path('change-username/', change_username, name='change_username'),
    path('change-email/', change_email, name='change_email'),
    path('change-password/', change_password, name='change_password'),
]