from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv

from .models import Subscriber, EmailList, Subscription, EmailTemplate, EmailSequence, SequenceStep, SentEmail


# ── Actions ──────────────────────────────────────────────────────────────────

@admin.action(description="Exportar seleccionados como CSV")
def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={modeladmin.model._meta.model_name}.csv"
    writer = csv.writer(response)
    # Headers dinámicos según el modelo
    model = modeladmin.model
    field_names = [f.name for f in model._meta.fields]
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, f) for f in field_names])
    return response


@admin.action(description="Activar seleccionados")
def activate_selected(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} activado(s).")


@admin.action(description="Desactivar seleccionados")
def deactivate_selected(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} desactivado(s).")


@admin.action(description="Reenviar emails fallidos")
def retry_failed(modeladmin, request, queryset):
    from crm.tasks import _send_sequence_email
    count = 0
    for sent in queryset.filter(status="failed"):
        try:
            _send_sequence_email(sent.subscriber_id, sent.template_id)
            sent.status = "sent"
            sent.save(update_fields=["status"])
            count += 1
        except Exception:
            pass
    modeladmin.message_user(request, f"{count} reenviado(s).")


# ── Inlines ──────────────────────────────────────────────────────────────────

class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    fields = ["email_list", "subscribed_at", "source"]
    readonly_fields = ["subscribed_at"]
    autocomplete_fields = ["email_list"]
    classes = ["collapse"]


class SequenceStepInline(admin.TabularInline):
    model = SequenceStep
    extra = 1
    fields = ["step_number", "template", "delay_days"]
    autocomplete_fields = ["template"]
    ordering = ["step_number"]
    classes = ["collapse"]


# ── ModelAdmins ──────────────────────────────────────────────────────────────

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "lists_summary", "is_active", "created_at", "sent_count"]
    list_filter = ["is_active", "created_at", "subscriptions__email_list"]
    search_fields = ["email", "name"]
    ordering = ["-created_at"]
    inlines = [SubscriptionInline]
    actions = [export_csv, activate_selected, deactivate_selected]
    list_select_related = False
    date_hierarchy = "created_at"

    def lists_summary(self, obj):
        lists = obj.subscriptions.select_related("email_list").all()
        return ", ".join(s.email_list.name for s in lists[:3]) + ("..." if len(lists) > 3 else "")
    lists_summary.short_description = "Listas"

    def sent_count(self, obj):
        return SentEmail.objects.filter(subscriber=obj, status="sent").count()
    sent_count.short_description = "Enviados"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("subscriptions__email_list")


@admin.register(EmailList)
class EmailListAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "subscriber_count", "sequences_count", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubscriptionInline]

    def subscriber_count(self, obj):
        return obj.subscribers.filter(subscriber__is_active=True).count()
    subscriber_count.short_description = "Suscriptores"

    def sequences_count(self, obj):
        return obj.sequences.count()
    sequences_count.short_description = "Secuencias"

    actions = [export_csv]

    class Media:
        css = {"all": ["admin/css/changelists.css"]}


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "subject_preview", "sequences_preview", "updated_at"]
    search_fields = ["name", "slug", "subject"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        ("Información", {"fields": ["name", "slug", "subject"]}),
        ("Contenido", {"fields": ["html_content", "plain_text_content"], "classes": ["wide"]}),
        ("Metadatos", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]
    actions = [export_csv]

    def subject_preview(self, obj):
        return obj.subject[:60] + ("..." if len(obj.subject) > 60 else "")
    subject_preview.short_description = "Asunto"

    def sequences_preview(self, obj):
        seqs = EmailSequence.objects.filter(steps__template=obj).distinct()
        return ", ".join(s.name for s in seqs[:2]) + ("..." if seqs.count() > 2 else "")
    sequences_preview.short_description = "Usado en"

    class Media:
        css = {"all": ["admin/css/widgets.css"]}


@admin.register(EmailSequence)
class EmailSequenceAdmin(admin.ModelAdmin):
    list_display = ["name", "email_list", "is_active", "steps_count", "created_at"]
    list_filter = ["is_active", "email_list"]
    search_fields = ["name"]
    inlines = [SequenceStepInline]
    actions = [activate_selected, deactivate_selected, export_csv]

    def steps_count(self, obj):
        return obj.steps.count()
    steps_count.short_description = "Pasos"


@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ["subscriber_email", "template_name", "sequence_name", "status", "sent_at"]
    list_filter = ["status", "sent_at", "template", "sequence"]
    search_fields = ["subscriber__email", "subscriber__name"]
    readonly_fields = ["sent_at"]
    date_hierarchy = "sent_at"
    actions = [export_csv, retry_failed]

    def subscriber_email(self, obj):
        return obj.subscriber.email
    subscriber_email.short_description = "Suscriptor"

    def template_name(self, obj):
        return obj.template.name
    template_name.short_description = "Plantilla"

    def sequence_name(self, obj):
        return obj.sequence.name if obj.sequence else "—"
    sequence_name.short_description = "Secuencia"
