from django.db import models
from django.conf import settings


CATEGORIA_DOC_CHOICES = [
    ('ebook',         'Endonautica (ebook)'),
    ('marco_teorico', 'Marco Teórico'),
    ('tradicion',     'Tradición / Sistema'),
]


class MirrorDocumento(models.Model):
    nombre      = models.CharField(max_length=200)
    categoria   = models.CharField(max_length=20, choices=CATEGORIA_DOC_CHOICES)
    autor_ref   = models.CharField(max_length=150, blank=True)
    procesado   = models.BooleanField(default=False)
    n_chunks    = models.PositiveIntegerField(default=0)
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['categoria', 'nombre']
        verbose_name = 'Documento Mirror KB'
        verbose_name_plural = 'Documentos Mirror KB'

    def __str__(self):
        return f"{self.nombre} [{self.categoria}]"


class MirrorChunk(models.Model):
    documento   = models.ForeignKey(MirrorDocumento, on_delete=models.CASCADE, related_name='chunks')
    categoria   = models.CharField(max_length=20, db_index=True)
    contenido   = models.TextField()
    embedding   = models.JSONField(null=True, blank=True)
    chunk_index = models.PositiveIntegerField()

    class Meta:
        ordering = ['documento', 'chunk_index']
        verbose_name = 'Chunk Mirror KB'

    def __str__(self):
        return f"Chunk {self.chunk_index} — {self.documento.nombre}"


class ConflictSession(models.Model):
    STATUS_CHOICES = [
        ('active',    'En curso'),
        ('completed', 'Completada'),
        ('archived',  'Archivada'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='conflict_sessions', null=True, blank=True
    )
    temp_profile = models.ForeignKey(
        'practitioners.TemporaryProfile', on_delete=models.CASCADE,
        related_name='conflict_sessions', null=True, blank=True
    )
    title = models.CharField(max_length=200, blank=True)
    conflict_description = models.TextField()
    messages = models.JSONField(default=list)
    pattern_revealed = models.TextField(blank=True)
    pregunta_cierre  = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        owner = self.user.email if self.user else str(self.temp_profile)
        return f'{owner} — {self.title or self.conflict_description[:50]}'

    def add_message(self, role, content):
        self.messages.append({'role': role, 'content': content})
        self.save()


class EspejoMemoria(models.Model):
    FUENTE_CHOICES = [
        ('perfil',       'Generada desde perfil'),
        ('sesion',       'Generada desde sesión'),
        ('restauracion', 'Restaurada por usuario'),
    ]
    user          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='espejo_memorias')
    version       = models.PositiveIntegerField()
    contenido     = models.TextField()
    activa        = models.BooleanField(default=False)
    fuente        = models.CharField(max_length=20, choices=FUENTE_CHOICES, default='sesion')
    sesion_origen = models.ForeignKey('ConflictSession', null=True, blank=True, on_delete=models.SET_NULL, related_name='memorias_generadas')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version']
        unique_together = [('user', 'version')]
        verbose_name = 'Memoria del Espejo'

    def __str__(self):
        return f'{self.user.email} v{self.version} ({self.fuente})'
