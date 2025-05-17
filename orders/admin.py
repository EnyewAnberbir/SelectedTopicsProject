from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'product_price', 'quantity', 'total_price')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'order_status', 'payment_status', 'total_price', 'created_at')
    list_filter = ('order_status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('order_number', 'user', 'shipping_address', 'billing_address', 'total_price', 'created_at')
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'created_at')
        }),
        ('Status', {
            'fields': ('order_status', 'payment_status')
        }),
        ('Payment', {
            'fields': ('total_price', 'shipping_cost', 'payment_method', 'payment_id')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'billing_address', 'tracking_number')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )
    inlines = [OrderItemInline]
    
    def has_add_permission(self, request):
        return False 