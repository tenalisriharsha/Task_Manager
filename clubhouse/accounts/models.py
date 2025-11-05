# File: accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def avatar_path(instance, filename):
    return f'avatars/user_{instance.user_id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to=avatar_path, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    points_total = models.IntegerField(default=0)
    stars_total = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    # Ensure a Profile exists for this User on every save (including login which updates last_login)
    profile, created_profile = Profile.objects.get_or_create(user=instance)
    # Initialize a friendly display name on first creation
    if created_profile and not profile.display_name:
        dn = (instance.get_full_name() or instance.username).strip()
        if dn:
            profile.display_name = dn
            profile.save(update_fields=['display_name'])
