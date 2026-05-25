from django.contrib import admin, messages
from .models import BirthProfile, BirthReport


def _get_timezone(lat, lng):
    try:
        from timezonefinder import TimezoneFinder
        tf = TimezoneFinder()
        return tf.timezone_at(lat=lat, lng=lng) or 'UTC'
    except Exception:
        return 'UTC'


@admin.action(description='🔄 Arreglar timezone + recalcular reportes')
def fix_and_recalc(modeladmin, request, queryset):
    from .calculators import calculate_astral_chart, calculate_hd_chart, calculate_saju_chart

    calc_map = {
        BirthReport.TYPE_ASTRAL: calculate_astral_chart,
        BirthReport.TYPE_HD:     calculate_hd_chart,
        BirthReport.TYPE_SAJU:   calculate_saju_chart,
    }

    fixed_tz = 0
    recalced = 0
    errors = []

    for bp in queryset:
        # 1. Fix timezone from coordinates
        if bp.latitude and bp.longitude:
            correct_tz = _get_timezone(bp.latitude, bp.longitude)
            if bp.timezone_str != correct_tz:
                bp.timezone_str = correct_tz
                bp.save(update_fields=['timezone_str'])
                fixed_tz += 1

        # 2. Regenerate every existing report (keep interpretation)
        for report in BirthReport.objects.filter(user=bp.user):
            calc_fn = calc_map.get(report.report_type)
            if not calc_fn:
                continue
            try:
                chart_data = calc_fn(bp)
                report.chart_data = chart_data
                report.status = BirthReport.STATUS_COMPLETE
                report.save(update_fields=['chart_data', 'status', 'updated_at'])
                recalced += 1
            except Exception as e:
                errors.append(f'{bp.user.email} / {report.report_type}: {e}')

    msg = f'Timezones corregidos: {fixed_tz}. Reportes recalculados: {recalced}.'
    if errors:
        msg += f' Errores: {"; ".join(errors)}'
        modeladmin.message_user(request, msg, level=messages.WARNING)
    else:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)


@admin.register(BirthProfile)
class BirthProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'birth_time', 'birth_place', 'timezone_str', 'latitude', 'longitude')
    search_fields = ('user__email', 'birth_place')
    actions = [fix_and_recalc]


@admin.register(BirthReport)
class BirthReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'report_type', 'status', 'created_at')
    list_filter = ('report_type', 'status')
    search_fields = ('user__email',)
