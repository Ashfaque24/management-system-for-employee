from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
import json
from datetime import datetime

from .models import (
    CustomUser, FormTemplate, FormField, Employee, 
    EmployeeCustomField, EmployeeDocument, EmployeeHistory
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, ChangePasswordSerializer,
    UserProfileSerializer, FormTemplateSerializer, FormTemplateCreateSerializer,
    FormFieldSerializer, EmployeeSerializer, EmployeeCreateSerializer,
    EmployeeUpdateSerializer, EmployeeCustomFieldSerializer,
    EmployeeDocumentSerializer, EmployeeHistorySerializer, EmployeeSearchSerializer
)

# ==================== WEB VIEWS ====================

def login_view(request):
    """Web login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'emp/login.html')

def register_view(request):
    """Web registration view"""
    if request.method == 'POST':
        # Handle registration logic
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'emp/register.html')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'emp/register.html')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'emp/register.html')
        
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        login(request, user)
        messages.success(request, 'Account created successfully!')
        return redirect('dashboard')
    
    return render(request, 'emp/register.html')

@login_required
def logout_view(request):
    """Web logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard_view(request):
    """Dashboard view"""
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='active').count()
    recent_employees = Employee.objects.order_by('-created_at')[:5]
    
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'recent_employees': recent_employees,
    }
    return render(request, 'emp/dashboard.html', context)

@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.address = request.POST.get('address', user.address)
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'emp/profile.html')

@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'emp/change_password.html')
        
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'emp/change_password.html')
        
        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, 'Password changed successfully!')
        return redirect('login')
    
    return render(request, 'emp/change_password.html')

# ==================== FORM MANAGEMENT VIEWS ====================

@login_required
def form_builder_view(request):
    """Dynamic form builder view"""
    if request.method == 'POST':
        form_data = json.loads(request.body)
        template_name = form_data.get('name')
        description = form_data.get('description', '')
        fields_data = form_data.get('fields', [])
        
        # Create form template
        template = FormTemplate.objects.create(
            name=template_name,
            description=description,
            created_by=request.user
        )
        
        # Create form fields
        for i, field_data in enumerate(fields_data):
            FormField.objects.create(
                form_template=template,
                label=field_data['label'],
                field_type=field_data['type'],
                required=field_data.get('required', False),
                placeholder=field_data.get('placeholder', ''),
                options=field_data.get('options'),
                order=i
            )
        
        return JsonResponse({'success': True, 'template_id': template.id})
    
    templates = FormTemplate.objects.filter(created_by=request.user)
    return render(request, 'emp/form_builder.html', {'templates': templates})

@login_required
def form_templates_view(request):
    """List form templates"""
    templates = FormTemplate.objects.filter(created_by=request.user)
    return render(request, 'emp/form_templates.html', {'templates': templates})

@login_required
def edit_form_template_view(request, template_id):
    """Edit form template"""
    template = get_object_or_404(FormTemplate, id=template_id, created_by=request.user)
    
    if request.method == 'POST':
        form_data = json.loads(request.body)
        template.name = form_data.get('name', template.name)
        template.description = form_data.get('description', template.description)
        template.save()
        
        # Update fields
        template.fields.all().delete()
        fields_data = form_data.get('fields', [])
        
        for i, field_data in enumerate(fields_data):
            FormField.objects.create(
                form_template=template,
                label=field_data['label'],
                field_type=field_data['type'],
                required=field_data.get('required', False),
                placeholder=field_data.get('placeholder', ''),
                options=field_data.get('options'),
                order=i
            )
        
        return JsonResponse({'success': True})
    
    return render(request, 'emp/edit_form_template.html', {'template': template})

# ==================== EMPLOYEE MANAGEMENT VIEWS ====================

@login_required
def employee_list_view(request):
    """Employee listing with search and filters"""
    employees = Employee.objects.all()
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(email__icontains=search) |
            Q(department__icontains=search)
        )
    
    # Filter by department
    department = request.GET.get('department')
    if department:
        employees = employees.filter(department=department)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        employees = employees.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique departments for filter dropdown
    departments = Employee.objects.values_list('department', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'departments': departments,
        'search': search,
        'department_filter': department,
        'status_filter': status_filter,
    }
    return render(request, 'emp/employee_list.html', context)

@login_required
def create_employee_view(request):
    """Create employee with dynamic form"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create employee
            employee = Employee.objects.create(
                employee_id=data['employee_id'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data['phone'],
                date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
                hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date(),
                department=data['department'],
                position=data['position'],
                salary=data['salary'],
                address_line1=data['address_line1'],
                address_line2=data.get('address_line2', ''),
                city=data['city'],
                state=data['state'],
                postal_code=data['postal_code'],
                country=data.get('country', 'United States'),
                emergency_contact_name=data['emergency_contact_name'],
                emergency_contact_phone=data['emergency_contact_phone'],
                emergency_contact_relationship=data['emergency_contact_relationship'],
                created_by=request.user
            )
            
            # Create custom fields if any
            custom_fields = data.get('custom_fields', {})
            for field_name, field_value in custom_fields.items():
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
                changed_by=request.user,
                description=f'Employee {employee.full_name} was created'
            )
            
            return JsonResponse({'success': True, 'employee_id': employee.id})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get form templates for dynamic form
    templates = FormTemplate.objects.filter(is_active=True)
    return render(request, 'emp/create_employee.html', {'templates': templates})

@login_required
def update_employee_view(request, employee_id):
    """Update employee"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Store old values for history
            old_values = {
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email,
                'phone': employee.phone,
                'department': employee.department,
                'position': employee.position,
                'salary': str(employee.salary),
                'status': employee.status,
            }
            
            # Update employee
            employee.employee_id = data['employee_id']
            employee.first_name = data['first_name']
            employee.last_name = data['last_name']
            employee.email = data['email']
            employee.phone = data['phone']
            employee.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
            employee.department = data['department']
            employee.position = data['position']
            employee.salary = data['salary']
            employee.status = data['status']
            employee.address_line1 = data['address_line1']
            employee.address_line2 = data.get('address_line2', '')
            employee.city = data['city']
            employee.state = data['state']
            employee.postal_code = data['postal_code']
            employee.country = data.get('country', 'United States')
            employee.emergency_contact_name = data['emergency_contact_name']
            employee.emergency_contact_phone = data['emergency_contact_phone']
            employee.emergency_contact_relationship = data['emergency_contact_relationship']
            employee.save()
            
            # Update custom fields
            custom_fields = data.get('custom_fields', {})
            employee.custom_fields.all().delete()
            for field_name, field_value in custom_fields.items():
                EmployeeCustomField.objects.create(
                    employee=employee,
                    field_name=field_name,
                    field_value=str(field_value),
                    field_type='text'
                )
            
            # Create history entry
            new_values = {
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email,
                'phone': employee.phone,
                'department': employee.department,
                'position': employee.position,
                'salary': str(employee.salary),
                'status': employee.status,
            }
            
            EmployeeHistory.objects.create(
                employee=employee,
                action='updated',
                changed_by=request.user,
                old_values=old_values,
                new_values=new_values,
                description=f'Employee {employee.full_name} was updated'
            )
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'emp/update_employee.html', {'employee': employee})

@login_required
def delete_employee_view(request, employee_id):
    """Delete employee"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        # Create history entry before deletion
        EmployeeHistory.objects.create(
            employee=employee,
            action='deleted',
            changed_by=request.user,
            description=f'Employee {employee.full_name} was deleted'
        )
        
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employee_list')
    
    return render(request, 'emp/delete_employee.html', {'employee': employee})

@login_required
def employee_detail_view(request, employee_id):
    """Employee detail view"""
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'emp/employee_detail.html', {'employee': employee})

# ==================== REST API VIEWS ====================

class UserRegistrationAPIView(APIView):
    """API view for user registration"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(APIView):
    """API view for user login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'success': True,
                'message': 'Login successful',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': UserProfileSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordAPIView(APIView):
    """API view for changing password"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'success': True,
                'message': 'Password changed successfully'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileAPIView(APIView):
    """API view for user profile"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FormTemplateListCreateAPIView(generics.ListCreateAPIView):
    """API view for form templates"""
    permission_classes = [IsAuthenticated]
    serializer_class = FormTemplateSerializer
    
    def get_queryset(self):
        return FormTemplate.objects.filter(created_by=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FormTemplateCreateSerializer
        return FormTemplateSerializer

class FormTemplateDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for form template detail"""
    permission_classes = [IsAuthenticated]
    serializer_class = FormTemplateSerializer
    
    def get_queryset(self):
        return FormTemplate.objects.filter(created_by=self.request.user)

class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    """API view for employees"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'status', 'hire_date']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email']
    ordering_fields = ['first_name', 'last_name', 'hire_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Employee.objects.all()
        
        # Custom field search
        custom_field_name = self.request.query_params.get('custom_field_name')
        custom_field_value = self.request.query_params.get('custom_field_value')
        
        if custom_field_name and custom_field_value:
            queryset = queryset.filter(
                custom_fields__field_name=custom_field_name,
                custom_fields__field_value__icontains=custom_field_value
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeCreateSerializer
        return EmployeeSerializer

class EmployeeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for employee detail"""
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeUpdateSerializer
        return EmployeeSerializer

class EmployeeSearchAPIView(APIView):
    """API view for advanced employee search"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = EmployeeSearchSerializer(data=request.data)
        if serializer.is_valid():
            queryset = Employee.objects.all()
            data = serializer.validated_data
            
            if data.get('search'):
                search_term = data['search']
                queryset = queryset.filter(
                    Q(first_name__icontains=search_term) |
                    Q(last_name__icontains=search_term) |
                    Q(employee_id__icontains=search_term) |
                    Q(email__icontains=search_term) |
                    Q(department__icontains=search_term)
                )
            
            if data.get('department'):
                queryset = queryset.filter(department=data['department'])
            
            if data.get('status'):
                queryset = queryset.filter(status=data['status'])
            
            if data.get('hire_date_from'):
                queryset = queryset.filter(hire_date__gte=data['hire_date_from'])
            
            if data.get('hire_date_to'):
                queryset = queryset.filter(hire_date__lte=data['hire_date_to'])
            
            if data.get('custom_field_name') and data.get('custom_field_value'):
                queryset = queryset.filter(
                    custom_fields__field_name=data['custom_field_name'],
                    custom_fields__field_value__icontains=data['custom_field_value']
                )
            
            serializer = EmployeeSerializer(queryset, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeDocumentAPIView(generics.ListCreateAPIView):
    """API view for employee documents"""
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeDocumentSerializer
    
    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        return EmployeeDocument.objects.filter(employee_id=employee_id)
    
    def perform_create(self, serializer):
        employee_id = self.kwargs.get('employee_id')
        serializer.save(
            employee_id=employee_id,
            uploaded_by=self.request.user
        )

class EmployeeHistoryAPIView(generics.ListAPIView):
    """API view for employee history"""
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeHistorySerializer
    
    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        return EmployeeHistory.objects.filter(employee_id=employee_id).order_by('-changed_at')
