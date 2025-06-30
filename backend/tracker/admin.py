from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Reading

# -----------------------------
# Inline Reading Admin
# -----------------------------
class ReadingInline(admin.TabularInline):
    model = Reading
    extra = 1
    readonly_fields = ('created_at', 'updated_at', 'get_blood_pressure_category', 'get_glucose_in_mg_dl')
    fields = ('systolic', 'diastolic', 'glucose_level', 'glucose_unit', 'notes', 'get_blood_pressure_category', 'get_glucose_in_mg_dl', 'created_at')
    can_delete = True
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return request.user.has_perm('readings.can_view_all_readings')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('readings.can_view_all_readings')

# -----------------------------
# Custom User Admin
# -----------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'age', 'weight', 'height')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),  # removed 'date_joined'
    )

    readonly_fields = ('last_login', 'date_joined')  # ✅ add date_joined here
    ordering = ('email',)
    search_fields = ('email',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

# -----------------------------
# Reading Admin
# -----------------------------
@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'systolic', 'diastolic', 'get_blood_pressure_category', 'glucose_level', 'glucose_unit', 'get_glucose_in_mmol_l', 'created_at')
    list_filter = ('glucose_unit', 'created_at', 'user')
    search_fields = ('user__email', 'notes', 'systolic', 'diastolic', 'glucose_level')
    ordering = ['-created_at']
    readonly_fields = ('created_at', 'updated_at', 'get_blood_pressure_category', 'get_glucose_in_mg_dl', 'get_glucose_in_mmol_l')
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('user', 'systolic', 'diastolic', 'glucose_level', 'glucose_unit', 'notes')
        }),
        (_('Calculated Values'), {
            'fields': ('get_blood_pressure_category', 'get_glucose_in_mg_dl', 'get_glucose_in_mmol_l'),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.has_perm('readings.can_view_all_readings'):
            return qs.filter(user=request.user)
        return qs

    def has_add_permission(self, request):
        return request.user.has_perm('readings.can_view_all_readings') or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        if obj and not request.user.has_perm('readings.can_view_all_readings'):
            return obj.user == request.user
        return super().has_change_permission(request, obj)