from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)
    raw_id_fields = ('product',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'id')
    date_hierarchy = 'date'
    ordering = ('-date',)
    inlines = [OrderItemInline]
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('total', 'date')
        return ('date',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')
    raw_id_fields = ('order', 'product')
    list_per_page = 20