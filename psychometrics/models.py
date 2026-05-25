from django.db import models
from django.conf import settings


class Test(models.Model):
    DIMENSION_CHOICES = [
        ('identidad',      'Identidad y Personalidad'),
        ('emociones',      'Emociones y Regulación'),
        ('cuerpo',         'Cuerpo y Sensorialidad'),
        ('mente',          'Mente y Aprendizaje'),
        ('vinculos',       'Vínculos y Apego'),
        ('sombra',         'Sombra y Patrones'),
        ('espiritualidad', 'Espiritualidad y Sentido'),
        ('suenos',         'Sueños y Conciencia'),
        ('proposito',      'Propósito y Trabajo'),
        ('comunidad',      'Comunidad y Relaciones'),
        ('abundancia',     'Abundancia y Finanzas'),
        ('creatividad',    'Creatividad e Integración'),
    ]

    INSTRUMENT_TYPE_CHOICES = [
        ('clinical', 'Instrumento Validado'),
        ('adapted',  'Adaptación de Instrumento Validado'),
        ('custom',   'Herramienta de Autoconocimiento'),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    dimension = models.CharField(max_length=30, choices=DIMENSION_CHOICES)
    instrument_type = models.CharField(max_length=20, choices=INSTRUMENT_TYPE_CHOICES, default='custom')
    description = models.TextField()
    instructions = models.TextField(blank=True)
    estimated_minutes = models.IntegerField(default=5)
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['dimension', 'order']

    def __str__(self):
        return self.name


class Question(models.Model):
    SCALE_CHOICES = [
        ('likert5',  'Likert 1-5 (frecuencia)'),
        ('likert5a', 'Likert 1-5 (acuerdo)'),   # BFI-44, TAS-20, Dirty Dozen
        ('likert4',  'Likert 0-4'),
        ('likert3',  'Likert 0-3'),              # GAD-7, PHQ-9, PSQI
        ('likert7',  'Likert 1-7'),              # SVI, ECR, SOC-29
        ('binary',   'Sí / No'),
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    dimension_key = models.CharField(max_length=80, blank=True)
    scale = models.CharField(max_length=10, choices=SCALE_CHOICES, default='likert5')
    reverse_scored = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'[{self.test.name}] {self.text[:60]}'


class TestResult(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='test_results', null=True, blank=True
    )
    temp_profile = models.ForeignKey(
        'practitioners.TemporaryProfile', on_delete=models.CASCADE,
        related_name='test_results', null=True, blank=True
    )
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    raw_scores = models.JSONField(default=dict)
    evaluation = models.JSONField(default=dict)
    ai_insight = models.TextField(blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        owner = self.user.email if self.user else str(self.temp_profile)
        return f'{owner} — {self.test.name}'
