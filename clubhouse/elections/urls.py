# File: elections/urls.py
from django.urls import path
from . import views

app_name = 'elections'

urlpatterns = [
    path('', views.current, name='current'),
    path('manage/', views.manage, name='manage'),
    path('create/', views.create_election, name='create'),
    path('vote/<int:election_id>/', views.vote, name='vote'),
    path('close/<int:election_id>/', views.close_election, name='close'),
]
