from django.db import models
from django.utils import timezone


class Subscriber(models.Model):
    """Contacto suscrito a una o más listas."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Suscriptor"
        verbose_name_plural = "Suscriptores"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>" if self.name else self.email


class EmailList(models.Model):
    """Lista de suscriptores (Mascara, Hacks, Viaje, etc.)."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lista de email"
        verbose_name_plural = "Listas de email"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def subscriber_count(self):
        return self.subscribers.filter(is_active=True).count()


class Subscription(models.Model):
    """Relación entre suscriptor y lista con metadata."""
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="subscriptions")
    email_list = models.ForeignKey(EmailList, on_delete=models.CASCADE, related_name="subscribers")
    subscribed_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=100, blank=True, help_text="Landing page de origen")

    class Meta:
        unique_together = ["subscriber", "email_list"]
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"

    def __str__(self):
        return f"{self.subscriber} → {self.email_list}"


class EmailTemplate(models.Model):
    """Plantilla de email HTML reusable."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    subject = models.CharField(max_length=255)
    html_content = models.TextField(help_text="HTML del email con {{ nombre }} para personalización")
    plain_text_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plantilla de email"
        verbose_name_plural = "Plantillas de email"
        ordering = ["name"]

    def __str__(self):
        return self.name


class EmailSequence(models.Model):
    """Secuencia de emails automatizada para una lista."""
    name = models.CharField(max_length=120)
    email_list = models.ForeignKey(EmailList, on_delete=models.CASCADE, related_name="sequences")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Secuencia de emails"
        verbose_name_plural = "Secuencias de emails"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.email_list})"


class SequenceStep(models.Model):
    """Paso individual en una secuencia de emails."""
    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE, related_name="steps")
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    delay_days = models.PositiveIntegerField(default=0, help_text="Días después del registro")

    class Meta:
        ordering = ["step_number"]
        unique_together = ["sequence", "step_number"]
        verbose_name = "Paso de secuencia"
        verbose_name_plural = "Pasos de secuencia"

    def __str__(self):
        return f"{self.sequence} - Paso {self.step_number} ({self.delay_days}d)"


class SentEmail(models.Model):
    """Registro de emails enviados."""
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="sent_emails")
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    sequence = models.ForeignKey(EmailSequence, on_delete=models.CASCADE, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ("pending", "Pendiente"),
        ("sent", "Enviado"),
        ("failed", "Fallido"),
    ], default="pending")
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = "Email enviado"
        verbose_name_plural = "Emails enviados"
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.template} → {self.subscriber} ({self.status})"


# ── Pipeline de Leads ──────────────────────────────────────────────────────────

class PipelineStage(models.Model):
    """Etapa del pipeline: visitante -> suscriptor -> trialer -> cliente."""
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Etapa del pipeline"
        verbose_name_plural = "Etapas del pipeline"
        ordering = ["order"]

    def __str__(self):
        return self.name


class PipelineLog(models.Model):
    """Registro de cuando un suscriptor cambia de etapa."""
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="pipeline_logs")
    stage = models.ForeignKey(PipelineStage, on_delete=models.CASCADE)
    entered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cambio de etapa"
        verbose_name_plural = "Cambios de etapa"
        ordering = ["-entered_at"]

    def __str__(self):
        return f"{self.subscriber} -> {self.stage} ({self.entered_at:%d/%m})"


class ContactNote(models.Model):
    """Nota interna sobre un suscriptor."""
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField()
    created_by = models.CharField(max_length=120, blank=True, help_text="Quien creo la nota")
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return f"Nota sobre {self.subscriber}: {self.content[:50]}..."


class Segment(models.Model):
    """Segmento para filtrar suscriptores por criterios."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    # Criterios almacenados como JSON: {"email_sent": true, "min_emails": 3, "list_slug": "mascara", ...}
    criteria = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Segmento"
        verbose_name_plural = "Segmentos"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_subscribers(self):
        """Aplica los criterios del segmento y devuelve un queryset."""
        from django.db.models import Count, Q
        qs = Subscriber.objects.filter(is_active=True)

        crit = self.criteria or {}
        if crit.get("list_slug"):
            qs = qs.filter(subscriptions__email_list__slug=crit["list_slug"])
        if crit.get("min_emails"):
            qs = qs.annotate(
                email_count=Count("sent_emails", filter=Q(sent_emails__status="sent"))
            ).filter(email_count__gte=crit["min_emails"])
        if crit.get("has_failed"):
            qs = qs.filter(sent_emails__status="failed").distinct()
        if crit.get("pipeline_stage"):
            from django.utils import timezone
            from datetime import timedelta
            qs = qs.filter(
                pipeline_logs__stage__slug=crit["pipeline_stage"],
                pipeline_logs__entered_at__gte=timezone.now() - timedelta(days=crit.get("stage_days", 30)),
            )
        return qs.distinct()


# ── Tags ──────────────────────────────────────────────────────────────────────

class Tag(models.Model):
    """Etiqueta para clasificar contactos (ej: interesado, cliente, frio, caliente)."""
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default="#c4813a", help_text="Color HEX para el badge")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ContactTag(models.Model):
    """Asignación de un tag a un suscriptor."""
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="contact_tags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="contact_tags")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["subscriber", "tag"]
        verbose_name = "Etiqueta de contacto"
        verbose_name_plural = "Etiquetas de contacto"

    def __str__(self):
        return f"{self.subscriber.email} → {self.tag.name}"


# ── Broadcasts (campañas manuales) ───────────────────────────────────────────

class Broadcast(models.Model):
    """Email puntual enviado manualmente a un segmento/lista."""
    name = models.CharField(max_length=200, help_text="Nombre interno de la campaña")
    subject = models.CharField(max_length=255)
    html_content = models.TextField()
    plain_text_content = models.TextField(blank=True)
    target_list = models.ForeignKey(EmailList, on_delete=models.SET_NULL, null=True, blank=True, related_name="broadcasts")
    target_segment = models.ForeignKey(Segment, on_delete=models.SET_NULL, null=True, blank=True, related_name="broadcasts")
    status = models.CharField(max_length=20, choices=[
        ("draft", "Borrador"),
        ("sending", "Enviando"),
        ("sent", "Enviado"),
        ("failed", "Fallido"),
    ], default="draft")
    total_recipients = models.PositiveIntegerField(default=0)
    total_sent = models.PositiveIntegerField(default=0)
    total_failed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Campaña manual"
        verbose_name_plural = "Campañas manuales"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"

