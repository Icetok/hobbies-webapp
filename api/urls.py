"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# api/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('hobbies/', views.hobbies_view, name='get_hobbies'),
    path('logout/', views.logout_view, name='logout'),
    path('auth-status/', views.auth_status, name='auth_status'),
    path('user-profile/', views.get_user_profile, name='get_user_profile'),
    path('similar-users/', views.get_similar_users, name='similar_users'),
    path('check-session/', views.check_session, name='check_session'),
    path('update-profile/', views.update_user_profile, name='update_user_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('friend-requests/send/', views.send_friend_request, name='send_friend_request'),
    path('friend-requests/respond/', views.respond_friend_request, name='respond_friend_request'),
    path('friend-requests/', views.list_friend_requests, name='list_friend_requests'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
