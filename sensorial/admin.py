from django.contrib import admin
from .models import BreathSession

@admin.register(BreathSession)
class BreathSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'pattern', 'cycles_completed', 'duration_seconds', 'started_at']
    list_filter = ['pattern']
