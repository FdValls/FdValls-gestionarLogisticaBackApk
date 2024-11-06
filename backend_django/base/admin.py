from django.contrib import admin
from base.models import Order, IdTemporal
# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [ 'order_id', 'phone_number', 'created_at' ]
    
@admin.register(IdTemporal)
class IdTemporalAdmin(admin.ModelAdmin):
    list_display = [ 'numero_id', 'created_at' ]