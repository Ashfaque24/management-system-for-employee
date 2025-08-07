from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    CustomUser, FormTemplate, FormField, Employee, 
    EmployeeCustomField, EmployeeDocument, EmployeeHistory
)

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 
                 'phone_number', 'address', 'date_of_birth')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password.')

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'address', 'profile_picture', 'date_of_birth', 
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class FormFieldSerializer(serializers.ModelSerializer):
    """Serializer for form fields"""
    class Meta:
        model = FormField
        fields = '__all__'

class FormTemplateSerializer(serializers.ModelSerializer):
    """Serializer for form templates"""
    fields = FormFieldSerializer(many=True, read_only=True)
    created_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = FormTemplate
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')

class FormTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating form templates with fields"""
    fields = FormFieldSerializer(many=True)
    
    class Meta:
        model = FormTemplate
        fields = ('name', 'description', 'is_active', 'fields')
    
    def create(self, validated_data):
        fields_data = validated_data.pop('fields')
        validated_data['created_by'] = self.context['request'].user
        form_template = FormTemplate.objects.create(**validated_data)
        
        for field_data in fields_data:
            FormField.objects.create(form_template=form_template, **field_data)
        
        return form_template

class EmployeeCustomFieldSerializer(serializers.ModelSerializer):
    """Serializer for employee custom fields"""
    class Meta:
        model = EmployeeCustomField
        fields = '__all__'

class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """Serializer for employee documents"""
    uploaded_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = EmployeeDocument
        fields = '__all__'
        read_only_fields = ('uploaded_by', 'uploaded_at')

class EmployeeHistorySerializer(serializers.ModelSerializer):
    """Serializer for employee history"""
    changed_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = EmployeeHistory
        fields = '__all__'
        read_only_fields = ('changed_by', 'changed_at')

class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for employee data"""
    created_by = UserProfileSerializer(read_only=True)
    custom_fields = EmployeeCustomFieldSerializer(many=True, read_only=True)
    documents = EmployeeDocumentSerializer(many=True, read_only=True)
    history = EmployeeHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['full_name'] = instance.full_name
        representation['full_address'] = instance.full_address
        return representation

class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating employees"""
    custom_fields = serializers.JSONField(required=False)
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        custom_fields_data = validated_data.pop('custom_fields', {})
        validated_data['created_by'] = self.context['request'].user
        employee = Employee.objects.create(**validated_data)
        
        # Create custom fields
        for field_name, field_value in custom_fields_data.items():
            EmployeeCustomField.objects.create(
                employee=employee,
                field_name=field_name,
                field_value=str(field_value),
                field_type='text'
            )
        
        # Create history entry
        EmployeeHistory.objects.create(
            employee=employee,
            action='created',
            changed_by=self.context['request'].user,
            description=f'Employee {employee.full_name} was created'
        )
        
        return employee

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating employees"""
    custom_fields = serializers.JSONField(required=False)
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def update(self, instance, validated_data):
        custom_fields_data = validated_data.pop('custom_fields', {})
        
        # Store old values for history
        old_values = {
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
            'phone': instance.phone,
            'department': instance.department,
            'position': instance.position,
            'salary': str(instance.salary),
            'status': instance.status,
        }
        
        # Update employee
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update custom fields
        if custom_fields_data:
            # Delete existing custom fields
            instance.custom_fields.all().delete()
            
            # Create new custom fields
            for field_name, field_value in custom_fields_data.items():
                EmployeeCustomField.objects.create(
                    employee=instance,
                    field_name=field_name,
                    field_value=str(field_value),
                    field_type='text'
                )
        
        # Create history entry
        new_values = {
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
            'phone': instance.phone,
            'department': instance.department,
            'position': instance.position,
            'salary': str(instance.salary),
            'status': instance.status,
        }
        
        EmployeeHistory.objects.create(
            employee=instance,
            action='updated',
            changed_by=self.context['request'].user,
            old_values=old_values,
            new_values=new_values,
            description=f'Employee {instance.full_name} was updated'
        )
        
        return instance

class EmployeeSearchSerializer(serializers.Serializer):
    """Serializer for employee search"""
    search = serializers.CharField(required=False)
    department = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    hire_date_from = serializers.DateField(required=False)
    hire_date_to = serializers.DateField(required=False)
    custom_field_name = serializers.CharField(required=False)
    custom_field_value = serializers.CharField(required=False)
