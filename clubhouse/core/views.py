# File: core/views.py
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.db import transaction
from accounts.forms import AdminUserEditForm, AdminProfileAdminForm, AdminPasswordForm
from .models import SiteSetting
from elections.models import Election
from accounts.models import Profile

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    settings = SiteSetting.get_solo()
    pending_profiles = Profile.objects.filter(is_approved=False).select_related('user')
    elections = Election.objects.order_by('-start_at')[:6]
    return render(request, 'core/admin_panel.html', {
        'settings': settings,
        'pending_profiles': pending_profiles,
        'elections': elections,
    })

@login_required
@user_passes_test(is_admin)
def rotate_join_code(request):
    settings = SiteSetting.get_solo()
    settings.join_code = get_random_string(8).upper()
    settings.save()
    messages.success(request, f'Join code rotated to: {settings.join_code}')
    return redirect('core:admin_panel')

@login_required
@user_passes_test(is_admin)
def set_first_leader(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    settings = SiteSetting.get_solo()
    settings.current_leader = u
    settings.save()
    messages.success(request, f'{u.get_username()} set as Leader.')
    return redirect('core:admin_panel')


# Admin member management views
@login_required
@user_passes_test(is_admin)
def members(request):
    qs = User.objects.select_related('profile').order_by('username')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(username__icontains=q)

    total = qs.count()
    approved = qs.filter(profile__is_approved=True).count()
    pending = qs.filter(profile__is_approved=False).count()

    return render(request, 'core/admin_members.html', {
        'members': qs,
        'total': total,
        'approved': approved,
        'pending': pending,
        'q': q,
    })

@login_required
@user_passes_test(is_admin)
@transaction.atomic
def member_edit(request, user_id):
    user = get_object_or_404(User.objects.select_related('profile'), pk=user_id)
    if request.method == 'POST':
        uform = AdminUserEditForm(request.POST, instance=user)
        pform = AdminProfileAdminForm(request.POST, instance=user.profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, f'Updated {user.username}.')
            return redirect('core:members')
    else:
        uform = AdminUserEditForm(instance=user)
        pform = AdminProfileAdminForm(instance=user.profile)
    return render(request, 'core/admin_member_edit.html', {
        'user_obj': user,
        'uform': uform,
        'pform': pform,
    })

@login_required
@user_passes_test(is_admin)
@transaction.atomic
def member_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = AdminPasswordForm(request.POST)
        if form.is_valid():
            pw = form.cleaned_data['new_password1']
            user.set_password(pw)
            user.save(update_fields=['password'])
            messages.success(request, f'Password reset for {user.username}.')
            return redirect('core:members')
    else:
        form = AdminPasswordForm()
    return render(request, 'core/admin_member_password.html', {
        'user_obj': user,
        'form': form,
    })

@login_required
@user_passes_test(is_admin)
@transaction.atomic
def member_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, "You cannot delete your own account.")
            return redirect('core:members')
        # Clear leader if this user is the current leader
        site = SiteSetting.get_solo()
        if site.current_leader_id == user.id:
            site.current_leader = None
            site.save(update_fields=['current_leader'])
        username = user.username
        user.delete()
        messages.success(request, f'Deleted {username}.')
        return redirect('core:members')
    return render(request, 'core/admin_member_delete_confirm.html', {
        'user_obj': user,
    })
