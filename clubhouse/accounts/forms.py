# File: accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import Profile

# Max avatar size per spec (2 MB)
MAX_AVATAR_SIZE = 2 * 1024 * 1024

class SignupForm(forms.ModelForm):
    # Extra fields not on the User model
    join_code = forms.CharField(
        max_length=32,
        required=False,
        help_text="Enter join code (if provided)"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        strip=False,
        help_text="Minimum per Django's password validators"
    )
    # Ensure proper email validation; keep optional
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Run Django's configured password validators
        validate_password(password)
        return password

    def clean_join_code(self):
        # Normalize whitespace for join code comparisons in view logic
        return self.cleaned_data.get('join_code', '').strip()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'avatar']

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar:
            return avatar
        # Enforce 2 MB size
        if hasattr(avatar, 'size') and avatar.size > MAX_AVATAR_SIZE:
            raise ValidationError("Avatar must be 2 MB or less.")
        # Basic content-type check (works for InMemoryUploadedFile)
        content_type = getattr(avatar, 'content_type', '')
        if content_type and not content_type.startswith('image/'):
            raise ValidationError("Please upload a valid image file (PNG or JPEG).")
        return avatar

# --- Admin member management forms ---
class AdminUserEditForm(forms.ModelForm):
    """Admin can edit basic User fields and active flag."""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']

class AdminProfileAdminForm(forms.ModelForm):
    """Admin can edit Profile flags and counters."""
    class Meta:
        model = Profile
        fields = ['display_name', 'is_approved', 'points_total', 'stars_total']

class AdminPasswordForm(forms.Form):
    """Admin sets a new password for a member."""
    new_password1 = forms.CharField(
        widget=forms.PasswordInput, strip=False, label="New password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput, strip=False, label="Confirm new password"
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match.")
        if p1:
            validate_password(p1)
        return cleaned
