from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        from tokens.models import TokenBalance
        TokenBalance.objects.create(
            user=instance,
            balance=settings.TOKEN_PLANS['free'].get('monthly_tokens', settings.TOKEN_PLANS['free'].get('monthly_fractones', 100))
        )
