from django.contrib import admin
from .models import Origin, HScode, HSTariff


class OriginAdmin(admin.ModelAdmin):
    list_display = ('origin_code', 'origin_name')
    search_fields = ('origin_code', 'origin_name')


class HScodeAdmin(admin.ModelAdmin):
    list_display = ('hs_code', 'hs_description')
    search_fields = ('hs_code', 'hs_description', 'hs_detailed')


class HSTariffAdmin(admin.ModelAdmin):
    list_display = ('hs_code_id', 'origin_id', 'tariff_rate')


admin.site.register(Origin, OriginAdmin)
admin.site.register(HScode, HScodeAdmin)
admin.site.register(HSTariff, HSTariffAdmin)
