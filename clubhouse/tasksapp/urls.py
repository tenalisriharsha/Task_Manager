# File: tasksapp/urls.py
from django.urls import path
from . import views

app_name = 'tasksapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('task/new/', views.task_new, name='task_new'),
    path('assignment/<int:pk>/submit/', views.assignment_submit, name='assignment_submit'),
    path('assignment/<int:pk>/approve/', views.assignment_approve, name='assignment_approve'),
    path('assignment/<int:pk>/star/', views.assignment_star, name='assignment_star'),
    path('history/', views.history, name='history'),
]
