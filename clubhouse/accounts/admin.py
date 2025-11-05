# File: accounts/admin.py
from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'is_approved', 'points_total', 'stars_total')
    search_fields = ('user__username', 'display_name')
    list_filter = ('is_approved',)
