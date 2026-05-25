from django.contrib import admin

from .models import Mission, MissionCompletion, TokenBalance, TokenTransaction


@admin.register(TokenBalance)
class TokenBalanceAdmin(admin.ModelAdmin):
    list_display   = ('user', 'permanent', 'monthly', 'balance_total', 'monthly_last_renewed', 'updated_at')
    search_fields  = ('user__email',)
    readonly_fields = ('balance_total', 'updated_at')

    def balance_total(self, obj):
        return obj.balance
    balance_total.short_description = 'Total'


@admin.register(TokenTransaction)
class TokenTransactionAdmin(admin.ModelAdmin):
    list_display  = ('user', 'amount', 'source', 'reason', 'created_at')
    list_filter   = ('source',)
    search_fields = ('user__email', 'reason')
    readonly_fields = ('created_at',)


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display   = ('name', 'slug', 'fracton_reward', 'order', 'active')
    list_editable  = ('order', 'active', 'fracton_reward')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MissionCompletion)
class MissionCompletionAdmin(admin.ModelAdmin):
    list_display  = ('user', 'mission', 'completed_at')
    search_fields = ('user__email', 'mission__slug')
    readonly_fields = ('completed_at',)
