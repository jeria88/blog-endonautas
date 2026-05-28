from django.db import models
from django.utils import timezone


class SetupItem(models.Model):
    CATEGORIA_CHOICES = [
        ('plataforma', 'Plataforma'),
        ('contenido', 'Contenido'),
    ]
    orden = models.IntegerField(default=0)
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES)
    texto = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    completado = models.BooleanField(default=False)
    completado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['categoria', 'orden']

    def __str__(self):
        return self.texto

    def toggle(self):
        self.completado = not self.completado
        self.completado_en = timezone.now() if self.completado else None
        self.save()


class Tarea(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En curso'),
        ('listo', 'Listo'),
    ]
    ETAPA_CHOICES = [
        ('0', 'Etapa 0'),
        ('1', 'Etapa 1'),
        ('2', 'Etapa 2'),
        ('backlog', 'Backlog'),
    ]
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    etapa = models.CharField(max_length=20, choices=ETAPA_CHOICES, default='0')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    orden = models.IntegerField(default=0)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['etapa', 'orden', 'creada_en']

    def __str__(self):
        return self.titulo


class PostContenido(models.Model):
    ESTADO_CHOICES = [
        ('generado', 'Generado'),
        ('programado', 'Programado'),
        ('publicado', 'Publicado'),
    ]
    TIPO_CHOICES = [
        ('carrusel', 'Carrusel'),
        ('texto', 'Texto'),
        ('articulo', 'Artículo'),
    ]
    codigo = models.CharField(max_length=10, blank=True)
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='generado')
    fecha_programada = models.DateField(null=True, blank=True)
    fecha_publicada = models.DateField(null=True, blank=True)
    cta_tipo = models.CharField(max_length=20, blank=True)
    notas = models.TextField(blank=True)

    class Meta:
        ordering = ['fecha_programada', 'estado']

    def __str__(self):
        return f"{self.codigo} — {self.titulo}"


class MetricaSemana(models.Model):
    semana = models.DateField(unique=True)
    seguidores_nuevos = models.IntegerField(default=0)
    saves_carrusel = models.IntegerField(default=0)
    comentarios_activos = models.IntegerField(default=0)
    pdfs_enviados = models.IntegerField(default=0)
    emails_abiertos_pct = models.IntegerField(default=0)
    registros_app = models.IntegerField(default=0)
    notas = models.TextField(blank=True)

    class Meta:
        ordering = ['-semana']

    def __str__(self):
        return f"Semana {self.semana}"


class IdeaCongelada(models.Model):
    texto = models.TextField()
    creada_en = models.DateTimeField(auto_now_add=True)
    revisada = models.BooleanField(default=False)

    class Meta:
        ordering = ['-creada_en']

    def __str__(self):
        return self.texto[:60]


class SesionRegistro(models.Model):
    TIPO_CHOICES = [
        ('quincenal', 'Sesión Quincenal'),
        ('semanal', 'Chequeo Semanal'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha = models.DateField()
    notas = models.TextField(blank=True)
    completada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.fecha}"
