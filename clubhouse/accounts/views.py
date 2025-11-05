# File: accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import SignupForm, ProfileForm
from core.models import SiteSetting

from django.db import transaction

def is_admin(user):
    return user.is_superuser or user.is_staff

def signup(request):
    """
    Sign up flow (invite-only + optional join code + admin approval):
    - If a join code is configured, it must match (otherwise show a form error and do not create the user).
    - Always create the account as pending (Profile.is_approved = False). Admin must approve separately.
    - Provide friendly errors for duplicate usernames/emails instead of raising IntegrityError.
    """
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            settings = SiteSetting.get_solo()
            join_code_input = form.cleaned_data.get('join_code', '').strip()

            # If a join code is configured, require it and validate
            if settings.join_code:
                if not join_code_input or join_code_input != settings.join_code:
                    form.add_error('join_code', 'Invalid join code.')
                    messages.error(request, 'Invalid join code.')
                    return render(request, 'accounts/signup.html', {'form': form})

            # Extract and remove password from cleaned_data to avoid passing raw password to create()
            password = form.cleaned_data.pop('password')
            form.cleaned_data.pop('join_code', None)

            # Friendly uniqueness checks
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'This username is already taken.')
                return render(request, 'accounts/signup.html', {'form': form})
            if email and User.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already registered.')
                return render(request, 'accounts/signup.html', {'form': form})

            # Create user and mark profile pending inside a single transaction
            with transaction.atomic():
                allowed = {
                    'username': form.cleaned_data.get('username'),
                    'email': form.cleaned_data.get('email'),
                    'first_name': form.cleaned_data.get('first_name'),
                    'last_name': form.cleaned_data.get('last_name'),
                }
                user = User.objects.create(is_active=True, **allowed)
                user.set_password(password)
                user.save()

                # Approval gating (always pending until admin approves)
                prof = user.profile  # created by post_save signal in accounts.models
                prof.is_approved = False
                prof.save()

            messages.info(request, 'Signup successful. Awaiting admin approval.')
            return redirect('accounts:pending')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def pending(request):
    return render(request, 'accounts/pending.html')

@login_required
def profile(request):
    prof = request.user.profile
    if not prof.is_approved:
        return redirect('accounts:pending')
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=prof)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=prof)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def approve_user(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    u.profile.is_approved = True
    u.profile.save()
    messages.success(request, f'Approved: {u.username}')
    return redirect('core:admin_panel')

@login_required
@user_passes_test(is_admin)
def deny_user(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    messages.info(request, f'Deleted: {u.username}')
    u.delete()
    return redirect('core:admin_panel')
