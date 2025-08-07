from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, FormTemplate, FormField, Employee, 
    EmployeeCustomField, EmployeeDocument, EmployeeHistory
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'address', 'profile_picture', 'date_of_birth')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'address', 'profile_picture', 'date_of_birth')}),
    )

class FormFieldInline(admin.TabularInline):
    """Inline admin for FormField"""
    model = FormField
    extra = 1
    fields = ('label', 'field_type', 'required', 'placeholder', 'order')

@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    """Admin interface for FormTemplate"""
    list_display = ('name', 'description', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    inlines = [FormFieldInline]

@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    """Admin interface for FormField"""
    list_display = ('label', 'form_template', 'field_type', 'required', 'order')
    list_filter = ('field_type', 'required', 'form_template')
    search_fields = ('label', 'form_template__name')
    ordering = ('form_template', 'order')

class EmployeeCustomFieldInline(admin.TabularInline):
    """Inline admin for EmployeeCustomField"""
    model = EmployeeCustomField
    extra = 1
    fields = ('field_name', 'field_value', 'field_type')

class EmployeeDocumentInline(admin.TabularInline):
    """Inline admin for EmployeeDocument"""
    model = EmployeeDocument
    extra = 1
    fields = ('document_type', 'title', 'file', 'description')

class EmployeeHistoryInline(admin.TabularInline):
    """Inline admin for EmployeeHistory"""
    model = EmployeeHistory
    extra = 0
    readonly_fields = ('action', 'changed_by', 'changed_at', 'description')
    can_delete = False

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin interface for Employee"""
    list_display = ('full_name', 'employee_id', 'email', 'department', 'position', 'status', 'hire_date')
    list_filter = ('status', 'department', 'hire_date', 'created_at')
    search_fields = ('first_name', 'last_name', 'employee_id', 'email', 'department')
    ordering = ('-created_at',)
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'profile_picture')
        }),
        ('Employment Details', {
            'fields': ('hire_date', 'department', 'position', 'salary', 'status')
        }),
        ('Address Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_active'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EmployeeCustomFieldInline, EmployeeDocumentInline, EmployeeHistoryInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new employee
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(EmployeeCustomField)
class EmployeeCustomFieldAdmin(admin.ModelAdmin):
    """Admin interface for EmployeeCustomField"""
    list_display = ('employee', 'field_name', 'field_value', 'field_type')
    list_filter = ('field_type', 'employee__department')
    search_fields = ('field_name', 'field_value', 'employee__first_name', 'employee__last_name')
    ordering = ('employee', 'field_name')

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    """Admin interface for EmployeeDocument"""
    list_display = ('employee', 'document_type', 'title', 'uploaded_by', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('title', 'employee__first_name', 'employee__last_name')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_by', 'uploaded_at')

@admin.register(EmployeeHistory)
class EmployeeHistoryAdmin(admin.ModelAdmin):
    """Admin interface for EmployeeHistory"""
    list_display = ('employee', 'action', 'changed_by', 'changed_at')
    list_filter = ('action', 'changed_at')
    search_fields = ('employee__first_name', 'employee__last_name', 'description')
    ordering = ('-changed_at',)
    readonly_fields = ('employee', 'action', 'changed_by', 'changed_at', 'old_values', 'new_values', 'description')
    can_delete = False
