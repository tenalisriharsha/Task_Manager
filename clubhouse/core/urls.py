# File: core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('rotate-join-code/', views.rotate_join_code, name='rotate_join_code'),
    path('set-first-leader/<int:user_id>/', views.set_first_leader, name='set_first_leader'),
    path('members/', views.members, name='members'),
    path('member/<int:user_id>/edit/', views.member_edit, name='member_edit'),
    path('member/<int:user_id>/password/', views.member_password, name='member_password'),
    path('member/<int:user_id>/delete/', views.member_delete, name='member_delete'),
]
