from django.contrib import admin
from .models import Payment, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'order', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('payment_id', 'user__email', 'order__order_number')
    readonly_fields = ('payment_id', 'user', 'order', 'amount', 'currency', 'payment_method', 'created_at')


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'reason')
    readonly_fields = ('order', 'payment', 'amount', 'created_at') 