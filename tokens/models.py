from datetime import date

from django.conf import settings
from django.db import models


class TokenBalance(models.Model):
    """
    Dos bolsillos:
      permanent  — fractones ganados (tests, misiones) + comprados. Nunca expiran.
      monthly    — recarga mensual del plan. Se reemplaza cada ciclo.
    Se gasta mensual primero, luego permanente.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='token_balance'
    )
    permanent = models.IntegerField(default=0)
    monthly   = models.IntegerField(default=0)
    monthly_last_renewed = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Balance de Fractones'

    def __str__(self):
        return f'{self.user.email}: {self.balance} fractones ({self.permanent}p + {self.monthly}m)'

    @property
    def balance(self):
        return self.permanent + self.monthly

    def spend(self, amount, reason=''):
        if self.balance < amount:
            return False
        if self.monthly >= amount:
            self.monthly -= amount
        else:
            remainder = amount - self.monthly
            self.monthly = 0
            self.permanent -= remainder
        self.save(update_fields=['monthly', 'permanent', 'updated_at'])
        TokenTransaction.objects.create(user=self.user, amount=-amount, reason=reason, source='spend')
        return True

    def credit_permanent(self, amount, reason=''):
        self.permanent += amount
        self.save(update_fields=['permanent', 'updated_at'])
        TokenTransaction.objects.create(user=self.user, amount=amount, reason=reason, source='permanent')

    def credit_monthly(self, amount, reason=''):
        self.monthly = amount
        self.monthly_last_renewed = date.today()
        self.save(update_fields=['monthly', 'monthly_last_renewed', 'updated_at'])
        TokenTransaction.objects.create(user=self.user, amount=amount, reason=reason, source='monthly')

    def credit(self, amount, reason=''):
        """Retrocompatibilidad — acredita permanente."""
        self.credit_permanent(amount, reason)


class TokenTransaction(models.Model):
    SOURCE_CHOICES = [
        ('permanent', 'Permanente'),
        ('monthly',   'Mensual'),
        ('spend',     'Gasto'),
    ]
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='token_transactions'
    )
    amount     = models.IntegerField()
    reason     = models.CharField(max_length=200, blank=True)
    source     = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='permanent')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transacción de Fractones'

    def __str__(self):
        sign = '+' if self.amount > 0 else ''
        return f'{self.user.email} {sign}{self.amount} [{self.source}] — {self.reason}'


class Mission(models.Model):
    slug           = models.CharField(max_length=60, unique=True)
    name           = models.CharField(max_length=120)
    description    = models.TextField(blank=True)
    fracton_reward    = models.IntegerField(default=0)
    prerequisite_slug = models.CharField(max_length=60, blank=True)
    order             = models.IntegerField(default=0)
    active            = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Misión'

    def __str__(self):
        return f'{self.name} (+{self.fracton_reward})'


class MissionCompletion(models.Model):
    user         = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mission_completions'
    )
    mission      = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'mission')
        verbose_name = 'Misión completada'

    def __str__(self):
        return f'{self.user.email} — {self.mission.name}'


class TokenPack(models.Model):
    """Producto Hotmart de pago único → recarga permanente."""
    name      = models.CharField(max_length=60)
    fractones = models.IntegerField(default=0)
    price_usd = models.DecimalField(max_digits=6, decimal_places=2)
    active    = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}: {self.fractones} fractones — ${self.price_usd}'
