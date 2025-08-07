from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
import json

class CustomUser(AbstractUser):
    """Extended User model with additional profile fields"""
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emp_customuser'
    
    def __str__(self):
        return self.username

class FormTemplate(models.Model):
    """Model for storing dynamic form templates"""
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('date', 'Date'),
        ('password', 'Password'),
        ('textarea', 'Text Area'),
        ('select', 'Select'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
        ('file', 'File Upload'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class FormField(models.Model):
    """Model for storing form fields within a template"""
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('date', 'Date'),
        ('password', 'Password'),
        ('textarea', 'Text Area'),
        ('select', 'Select'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
        ('file', 'File Upload'),
    ]
    
    form_template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=200, blank=True, null=True)
    options = models.JSONField(blank=True, null=True)  # For select, radio fields
    order = models.IntegerField(default=0)
    validation_rules = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.form_template.name} - {self.label}"

class Employee(models.Model):
    """Enhanced Employee model with dynamic fields support"""
    EMPLOYMENT_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('resigned', 'Resigned'),
    ]
    
    # Core fields
    employee_id = models.CharField(max_length=50, unique=True, validators=[MinLengthValidator(3)])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    hire_date = models.DateField()
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='active')
    
    # Address information
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    
    # Additional information
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=15)
    emergency_contact_relationship = models.CharField(max_length=100)
    
    # System fields
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_employees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Profile picture
    profile_picture = models.ImageField(upload_to='employee_pics/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        address_parts.extend([self.city, self.state, self.postal_code, self.country])
        return ', '.join(address_parts)

class EmployeeCustomField(models.Model):
    """Model for storing custom field values for employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='custom_fields')
    field_name = models.CharField(max_length=200)
    field_value = models.TextField()
    field_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'field_name']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.field_name}"

class EmployeeDocument(models.Model):
    """Model for storing employee documents"""
    DOCUMENT_TYPES = [
        ('contract', 'Employment Contract'),
        ('id_proof', 'ID Proof'),
        ('resume', 'Resume'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='employee_documents/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"

class EmployeeHistory(models.Model):
    """Model for tracking employee history changes"""
    ACTION_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('status_changed', 'Status Changed'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.action} by {self.changed_by.username}"