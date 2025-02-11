from .models import CreditCard
from django.contrib import admin


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_editable = ['status']
    list_display = ['user', 'card_number', 'card_type', 'credit_limit', 'status', 'created_at', 'updated_at']
    list_filter = ['user', 'status', 'created_at', 'updated_at']
    search_fields = ['user__email', 'card_number']
    readonly_fields = ['card_number', 'created_at', 'updated_at']
