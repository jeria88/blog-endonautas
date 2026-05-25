from django.contrib import admin
from .models import BackgroundTemplate, TemplateRating


@admin.register(BackgroundTemplate)
class BackgroundTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_public', 'use_count', 'avg_rating', 'created_at')
    list_filter = ('is_public',)
    search_fields = ('name', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'use_count')


@admin.register(TemplateRating)
class TemplateRatingAdmin(admin.ModelAdmin):
    list_display = ('template', 'user', 'score')
