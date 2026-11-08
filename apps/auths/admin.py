from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.decorators import action, display
from unfold.forms import AdminPasswordChangeForm


from apps.auths.models import User
from apps.auths.forms import CustomUserChangeForm, CustomUserCreationForm 


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ( "user_header", "active_label", "staff_label", "posts_count")
    list_filter = [
        ("is_active", BooleanRadioFilter),
        ("is_staff", BooleanRadioFilter),
    ]
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    actions = ["activate_users", "deactivate_users"]
    fieldsets = (
        ("Personal info", {
            "classes": ["tab"],
            "fields": ("email", "first_name", "last_name"),
        }),
        ("Permissions", {
            "classes": ["tab"],
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Important dates", {
            "classes": ["tab"],
            "fields": ("last_login", "date_joined"),
        }), 
        )
    add_fieldsets = (
        (None, {
            "classes": ["wide"],
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )


    def get_queryset(self, request):
        return super().get_queryset(request).annotate(posts_count=Count("posts"))

    @display(description="User", header=True)
    def user_header(self, obj):
        initials = (obj.first_name[:1] + obj.last_name[:1].upper() or obj.email[:1].upper())
        full_name = f"{obj.first_name} {obj.last_name}".strip() or obj.email
        return [full_name, obj.email, initials]

    @display(description="Active", ordering="is_active", label = {"yes": "success", "no": "danger"})
    def active_label(self, obj):
        if obj.is_active:
            return "Yes", "Active"
        return "No", "Inactive"

    @display(description="Staff", ordering="is_staff", label = {"yes": "info", "no": "warning"})
    def staff_label(self, obj):
        if obj.is_staff:
            return "Yes", "Staff"
        return "No", "Not Staff"

    @display(description="Posts", ordering="posts_count")
    def posts_count(self, obj):
        return obj.posts_total

    @action (description="Activate selected users")
    def activate_users(self, request, queryset):
        updated_count = queryset.update(is_active=True)
        self.message_user(request, f"activated users: {updated}", messages.SUCCESS)

    @action (description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        updated_count = queryset.update(is_active=False)
        self.message_user(request, f"deactivated users: {updated}", messages.SUCCESS)


    admin.site.unregister(Group)

    @admin.register(Group)
    class GroupAdmin(BaseGroupAdmin, ModelAdmin):
        pass