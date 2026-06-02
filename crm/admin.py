from django.contrib import admin
from .models import Subscriber, EmailList, Subscription, EmailTemplate, EmailSequence, SequenceStep, SentEmail


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["email", "name"]


@admin.register(EmailList)
class EmailListAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "subscriber_count", "created_at"]
    prepopulated_fields = {"slug": ("name",)}


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "subject", "updated_at"]
    prepopulated_fields = {"slug": ("name",)}


class SequenceStepInline(admin.TabularInline):
    model = SequenceStep
    extra = 0


@admin.register(EmailSequence)
class EmailSequenceAdmin(admin.ModelAdmin):
    list_display = ["name", "email_list", "is_active", "created_at"]
    list_filter = ["is_active", "email_list"]
    inlines = [SequenceStepInline]


@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ["subscriber", "template", "sent_at", "status"]
    list_filter = ["status", "sent_at"]
    search_fields = ["subscriber__email"]
    readonly_fields = ["sent_at"]
