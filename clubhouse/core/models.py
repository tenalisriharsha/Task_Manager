# File: core/models.py
from django.db import models
from django.contrib.auth.models import User

class SiteSetting(models.Model):
    """Singleton settings row."""
    join_code = models.CharField(max_length=32, blank=True, default='')
    current_leader = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='leader_of'
    )

    def __str__(self):
        return "Site Settings (singleton)"

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
