from django.db import models
from django.conf import settings


class BreathSession(models.Model):
    PATTERN_COHERENCIA = 'coherencia'
    PATTERN_CAJA = 'caja'
    PATTERN_RELAX = 'relax'
    PATTERN_CHOICES = [
        (PATTERN_COHERENCIA, 'Coherencia Cardíaca'),
        (PATTERN_CAJA, 'Respiración en Caja'),
        (PATTERN_RELAX, 'Relajación 4-7-8'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='breath_sessions')
    pattern = models.CharField(max_length=20, choices=PATTERN_CHOICES)
    cycles_completed = models.PositiveIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user} — {self.pattern} ({self.cycles_completed} ciclos)'
