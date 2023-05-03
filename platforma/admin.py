from django.contrib import admin
from .models import Origin, HScode, HSTariff, Item, Distributor, Forwarder, Customer, ContractDelivery


class OriginAdmin(admin.ModelAdmin):
    list_display = ('origin_code', 'origin_name')
    search_fields = ('origin_code', 'origin_name')


class HScodeAdmin(admin.ModelAdmin):
    list_display = ('hs_code', 'hs_description')
    search_fields = ('hs_code', 'hs_description', 'hs_detailed')


class HSTariffAdmin(admin.ModelAdmin):
    list_display = ('hs_code_id', 'origin_id', 'tariff_rate')


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price')
    raw_id_fields = ('hs_tariff_id',)


class DistributorAdmin(admin.ModelAdmin):
    list_display = ('distributor_user', 'company_name', 'registration_code', 'address')


class ForwarderAdmin(admin.ModelAdmin):
    list_display = ('forwarder_user', 'company_name', 'registration_code', 'address')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_user', 'name', 'address')


class ContractDeliveryAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'region', 'freight_cost_vkg', 'distributor_id', 'forwarder_id')


admin.site.register(Origin, OriginAdmin)
admin.site.register(HScode, HScodeAdmin)
admin.site.register(HSTariff, HSTariffAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Distributor, DistributorAdmin)
admin.site.register(Forwarder, ForwarderAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(ContractDelivery, ContractDeliveryAdmin)
