from django.db import models
from django.conf import settings
import uuid


class TemporaryProfile(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profiles'
    )
    alias = models.CharField(max_length=80)
    notes = models.TextField(blank=True)
    access_code = models.UUIDField(default=uuid.uuid4, unique=True)
    claimed_by = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='claimed_profile'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.alias} (de {self.created_by.email})'
