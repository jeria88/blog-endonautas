from django.db import models
from django.conf import settings


class BackgroundTemplate(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bg_templates')
    name        = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    prompt_used = models.TextField(blank=True)

    # JSON: {general: html, espejo: html, tests: html, onboarding: html, birth: html}
    scenes      = models.JSONField(default=dict)
    # JSON: {general_to_espejo: "dissolve", general_to_tests: "fade", ...}
    transitions = models.JSONField(default=dict)
    # List of image/video URLs used
    media_urls  = models.JSONField(default=list)

    is_public   = models.BooleanField(default=False)
    use_count   = models.PositiveIntegerField(default=0)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.user.email})'

    @property
    def avg_rating(self):
        ratings = self.ratings.all()
        if not ratings:
            return 0
        return round(sum(r.score for r in ratings) / len(ratings), 1)


class TemplateRating(models.Model):
    template = models.ForeignKey(BackgroundTemplate, on_delete=models.CASCADE, related_name='ratings')
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='template_ratings')
    score    = models.PositiveSmallIntegerField()  # 1-5

    class Meta:
        unique_together = [('template', 'user')]

    def __str__(self):
        return f'{self.user.email} → {self.template.name} ({self.score}★)'
