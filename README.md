# Employee Management System (EMS Pro)

A comprehensive Employee Management System built with Django, featuring dynamic form creation, REST API, JWT authentication, and modern web interface.

## 🚀 Features

### Authentication & Profile Management
- **User Registration & Login**: Secure user authentication system
- **JWT Token Authentication**: Access and refresh tokens for API security
- **Profile Management**: User profile updates and password changes
- **Role-based Access Control**: Different permissions for different user types

### Dynamic Form Builder
- **Drag & Drop Interface**: Intuitive form building with drag-and-drop functionality
- **Multiple Field Types**: Text, Number, Email, Date, Password, Textarea, Select, Checkbox, Radio, File Upload
- **Custom Validation**: Built-in validation rules and custom validation support
- **Form Templates**: Save and reuse form templates
- **Real-time Preview**: Live preview of form fields as you build

### Employee Management
- **Comprehensive Employee Records**: Complete employee information management
- **Dynamic Fields**: Custom fields based on form templates
- **Document Management**: Upload and manage employee documents
- **History Tracking**: Complete audit trail of employee changes
- **Advanced Search**: Search and filter employees with multiple criteria
- **Bulk Operations**: Efficient handling of multiple employees

### REST API
- **Complete CRUD Operations**: Full Create, Read, Update, Delete functionality
- **JWT Authentication**: Secure API access with token-based authentication
- **Filtering & Pagination**: Advanced filtering, searching, and pagination
- **File Upload Support**: Handle document uploads via API
- **Comprehensive Documentation**: Complete API documentation with examples

### Modern Web Interface
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Bootstrap 5**: Modern, clean, and professional UI
- **Interactive Charts**: Dashboard with employee statistics and charts
- **Real-time Updates**: AJAX-powered interface for smooth user experience
- **Dark/Light Theme Support**: Customizable interface themes

## 🛠️ Technology Stack

- **Backend**: Django 4.1.7, Python 3.8+
- **Database**: SQLite (development) / MySQL (production)
- **API**: Django REST Framework 3.14.0
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Libraries**: Axios, Chart.js, Sortable.js, Font Awesome
- **Development**: Virtual Environment, Git

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- MySQL (optional, for production)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/employee-management-system.git
cd employee-management-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## 📖 Usage

### Web Interface

1. **Access the Application**: Navigate to `http://localhost:8000`
2. **Register/Login**: Create an account or login with existing credentials
3. **Dashboard**: View employee statistics and recent activities
4. **Form Builder**: Create custom forms using the drag-and-drop interface
5. **Employee Management**: Add, edit, and manage employee records
6. **Search & Filter**: Use advanced search and filtering options

### API Usage

#### Authentication
```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login to get access token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

#### Employee Management
```bash
# Get all employees
curl -X GET http://localhost:8000/api/employees/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Create new employee
curl -X POST http://localhost:8000/api/employees/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "department": "IT",
    "position": "Software Developer",
    "salary": "75000.00"
  }'
```

#### Form Templates
```bash
# Create form template
curl -X POST http://localhost:8000/api/forms/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Employee Onboarding",
    "description": "Form for new employees",
    "fields": [
      {
        "label": "Full Name",
        "field_type": "text",
        "required": true
      }
    ]
  }'
```

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | User login |
| POST | `/api/auth/change-password/` | Change password |
| GET | `/api/auth/profile/` | Get user profile |
| PUT | `/api/auth/profile/` | Update user profile |

### Employee Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees/` | Get all employees |
| POST | `/api/employees/` | Create new employee |
| GET | `/api/employees/{id}/` | Get employee by ID |
| PUT | `/api/employees/{id}/` | Update employee |
| DELETE | `/api/employees/{id}/` | Delete employee |
| POST | `/api/employees/search/` | Advanced search |

### Form Template Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/forms/` | Get all form templates |
| POST | `/api/forms/` | Create form template |
| GET | `/api/forms/{id}/` | Get form template by ID |
| PUT | `/api/forms/{id}/` | Update form template |
| DELETE | `/api/forms/{id}/` | Delete form template |

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees/{id}/documents/` | Get employee documents |
| POST | `/api/employees/{id}/documents/` | Upload document |

### History Tracking

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees/{id}/history/` | Get employee history |

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
For MySQL production setup, update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📦 Deployment

### Production Setup
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Configure web server (Nginx/Apache)
5. Set up SSL certificates

### Docker Deployment
```bash
# Build Docker image
docker build -t ems-pro .

# Run container
docker run -p 8000:8000 ems-pro
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Email: support@emspro.com
- Documentation: [docs.emspro.com](https://docs.emspro.com)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the responsive UI components
- All contributors who helped improve this project

## 📊 Project Status

- ✅ Core functionality implemented
- ✅ API endpoints complete
- ✅ Frontend interface ready
- ✅ Documentation updated
- 🔄 Additional features in development
- 🔄 Mobile app planned

---

**Made with ❤️ by the EMS Pro Team**
