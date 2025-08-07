from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API views
router = DefaultRouter()

# Web URLs
urlpatterns = [
    # Authentication URLs
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/change-password/', views.change_password_view, name='change_password'),
    
    # Dashboard and Profile
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Form Management URLs
    path('forms/builder/', views.form_builder_view, name='form_builder'),
    path('forms/templates/', views.form_templates_view, name='form_templates'),
    path('forms/templates/<int:template_id>/edit/', views.edit_form_template_view, name='edit_form_template'),
    
    # Employee Management URLs
    path('employees/', views.employee_list_view, name='employee_list'),
    path('employees/create/', views.create_employee_view, name='create_employee'),
    path('employees/<int:employee_id>/', views.employee_detail_view, name='employee_detail'),
    path('employees/<int:employee_id>/update/', views.update_employee_view, name='update_employee'),
    path('employees/<int:employee_id>/delete/', views.delete_employee_view, name='delete_employee'),
    
    # API URLs
    path('api/', include([
        # Authentication API
        path('auth/register/', views.UserRegistrationAPIView.as_view(), name='api_register'),
        path('auth/login/', views.UserLoginAPIView.as_view(), name='api_login'),
        path('auth/change-password/', views.ChangePasswordAPIView.as_view(), name='api_change_password'),
        path('auth/profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
        
        # Form Template API
        path('forms/', views.FormTemplateListCreateAPIView.as_view(), name='api_form_templates'),
        path('forms/<int:pk>/', views.FormTemplateDetailAPIView.as_view(), name='api_form_template_detail'),
        
        # Employee API
        path('employees/', views.EmployeeListCreateAPIView.as_view(), name='api_employees'),
        path('employees/<int:pk>/', views.EmployeeDetailAPIView.as_view(), name='api_employee_detail'),
        path('employees/search/', views.EmployeeSearchAPIView.as_view(), name='api_employee_search'),
        path('employees/<int:employee_id>/documents/', views.EmployeeDocumentAPIView.as_view(), name='api_employee_documents'),
        path('employees/<int:employee_id>/history/', views.EmployeeHistoryAPIView.as_view(), name='api_employee_history'),
    ])),
]
