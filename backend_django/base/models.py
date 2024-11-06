from django.db import models

class Order(models.Model):
    order_id = models.CharField(max_length=100,  unique=True, verbose_name='order_id')
    phone_number = models.CharField(max_length=20, verbose_name='phone_number')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')
    
    class Meta:
        db_table = 'base_order'
        verbose_name = 'order'
        verbose_name_plural = 'orders'

    def __str__(self):
        return f"Order {self.order_id} - {self.phone_number}"

class IdTemporal(models.Model):
    numero_id = models.CharField(max_length=20, unique=True, verbose_name='numero_id')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')
    
    class Meta:
        db_table = 'temporal'
        verbose_name = 'ID temporal'
        verbose_name_plural = 'ID temporales'

    def __str__(self):
        return f"{self.numero_id}"
