from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'


class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('navegante', 'Navegante — $10/mes'),
        ('practicante', 'Facilitador — $39/mes'),
        ('empresa', 'Empresa'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    plan_active_since = models.DateField(null=True, blank=True)
    hotmart_subscriber_code = models.CharField(max_length=120, blank=True)
    tokens_last_renewed = models.DateField(null=True, blank=True)
    MAP_AESTHETIC_CHOICES = [
        ('cosmos',      'Cósmico'),
        ('mandala',     'Geometría Sagrada'),
        ('psychedelic', 'Psicodélico'),
    ]
    map_aesthetic = models.CharField(max_length=20, choices=MAP_AESTHETIC_CHOICES, blank=True, default='')

    bio = models.TextField(blank=True)
    profession = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    profile_public = models.BooleanField(default=False)
    active_template = models.ForeignKey(
        'background.BackgroundTemplate', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='active_users'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    onboarding_entry_point = models.CharField(max_length=80, blank=True)
    onboarding_noise_area = models.CharField(max_length=80, blank=True)
    onboarding_prior_exploration = models.CharField(max_length=300, blank=True)
    onboarding_question = models.TextField(blank=True)
    onboarding_nucleo = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'{self.user.email} [{self.plan}]'

    @property
    def plan_config(self):
        return settings.TOKEN_PLANS.get(self.plan, settings.TOKEN_PLANS['free'])

    @property
    def is_practicante(self):
        return self.plan in ('practicante', 'empresa')
