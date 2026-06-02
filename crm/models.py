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
