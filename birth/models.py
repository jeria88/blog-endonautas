from django.db import models
from django.conf import settings


SIGN_ES = {
    'Ari': 'Aries', 'Tau': 'Tauro', 'Gem': 'Géminis', 'Can': 'Cáncer',
    'Leo': 'Leo', 'Vir': 'Virgo', 'Lib': 'Libra', 'Sco': 'Escorpio',
    'Sag': 'Sagitario', 'Cap': 'Capricornio', 'Aqu': 'Acuario', 'Pis': 'Piscis',
}

HOUSE_NUM = {
    'First_House': 1, 'Second_House': 2, 'Third_House': 3, 'Fourth_House': 4,
    'Fifth_House': 5, 'Sixth_House': 6, 'Seventh_House': 7, 'Eighth_House': 8,
    'Ninth_House': 9, 'Tenth_House': 10, 'Eleventh_House': 11, 'Twelfth_House': 12,
}

PLANET_SYMBOLS = {
    'sun': '☉', 'moon': '☽', 'mercury': '☿', 'venus': '♀', 'mars': '♂',
    'jupiter': '♃', 'saturn': '♄', 'uranus': '♅', 'neptune': '♆', 'pluto': '♇',
}

SIGN_SYMBOLS = {
    'Aries': '♈', 'Tauro': '♉', 'Géminis': '♊', 'Cáncer': '♋',
    'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Escorpio': '♏',
    'Sagitario': '♐', 'Capricornio': '♑', 'Acuario': '♒', 'Piscis': '♓',
}

SIGN_ELEMENT = {
    'Aries': 'fire', 'Leo': 'fire', 'Sagitario': 'fire',
    'Tauro': 'earth', 'Virgo': 'earth', 'Capricornio': 'earth',
    'Géminis': 'air', 'Libra': 'air', 'Acuario': 'air',
    'Cáncer': 'water', 'Escorpio': 'water', 'Piscis': 'water',
}


class BirthProfile(models.Model):
    GENDER_MALE   = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = [('M', 'Masculino'), ('F', 'Femenino')]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='birth_profile'
    )
    birth_date = models.DateField()
    birth_time = models.TimeField(null=True, blank=True)
    birth_place = models.CharField(max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timezone_str = models.CharField(max_length=60, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.email} — {self.birth_place} {self.birth_date}'


class BirthReport(models.Model):
    TYPE_ASTRAL = 'astral'
    TYPE_SAJU = 'saju'
    TYPE_HD = 'human_design'
    REPORT_TYPES = [
        (TYPE_ASTRAL, 'Carta Astral'),
        (TYPE_SAJU, 'Saju'),
        (TYPE_HD, 'Diseño Humano'),
    ]
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETE = 'complete'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_PROCESSING, 'Procesando'),
        (STATUS_COMPLETE, 'Completo'),
        (STATUS_FAILED, 'Error'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    chart_data = models.JSONField(null=True, blank=True)
    interpretation = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'report_type')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} — {self.report_type} [{self.status}]'
