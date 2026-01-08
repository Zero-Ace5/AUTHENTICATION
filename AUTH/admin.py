from django.contrib import admin
from .models import User, UserDeviceSession


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # We use admin.ModelAdmin because AbstractBaseUser doesn't
    # automatically include groups/permissions fields
    list_display = ('email', 'name', 'user_type', 'created_at', 'last_login')
    list_filter = ('user_type', 'created_at')
    search_fields = ('email', 'name')
    ordering = ('-created_at',)

    # Custom fields layout for your specific model
    fieldsets = (
        (None, {'fields': ('email', 'name', 'user_type')}),
        ('Status', {'fields': ('last_login', 'created_at')}),
    )
    readonly_fields = ('created_at', 'last_login')


@admin.register(UserDeviceSession)
class UserDeviceSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'user_agent_short',
                    'last_activity', 'is_active')
    list_filter = ('is_active', 'last_activity')
    search_fields = ('user__email', 'ip_address', 'jti')
    readonly_fields = ('jti', 'created_at', 'last_activity')

    def user_agent_short(self, obj):
        return obj.user_agent[:50] + "..." if len(obj.user_agent) > 50 else obj.user_agent
    user_agent_short.short_description = "Device Info"
