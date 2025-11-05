# File: accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('pending/', views.pending, name='pending'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('accounts:login')), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('deny/<int:user_id>/', views.deny_user, name='deny_user'),
]
