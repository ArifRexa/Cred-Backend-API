from django.contrib import admin

from users.models import CustomUser

admin.site.site_header = "Credit Card Admin"
admin.site.site_title = "Credit Card Admin"
admin.site.index_title = "Welcome to Credit Card Admin"

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'role']
    list_filter = ['role', 'email']
    list_editable = ['role']
    search_fields = ['email', 'role']
    readonly_fields = ['date_joined', 'last_login']
