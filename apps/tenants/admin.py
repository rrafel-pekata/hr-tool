from django.contrib import admin

from .models import Company, CompanyMembership, Department, UserProfile


@admin.action(description='Restaurar seleccionados')
def restore_selected(modeladmin, request, queryset):
    queryset.update(deleted_at=None)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'deleted_at', 'created_at')
    list_filter = ('is_active', 'deleted_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    actions = [restore_selected]

    def get_queryset(self, request):
        return Company.all_objects.all()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role')
    list_filter = ('role', 'company')
    search_fields = ('user__username', 'user__email', 'company__name')


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role')
    list_filter = ('role', 'company')
    search_fields = ('user__username', 'user__email', 'company__name')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'created_at')
    list_filter = ('company',)
    search_fields = ('name', 'company__name')
