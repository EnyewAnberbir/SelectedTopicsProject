# 🛍️ E-Commerce API Testing & Automation with Postman
A feature-rich Django REST Framework backend for e-commerce and an automated Postman testing suite — combining backend API development and end-to-end API testing.

##          📌 Project Overview
This project showcases API testing and automation for a fully functional e-commerce backend built with Django REST Framework. Using Postman and Newman CLI, it ensures the API is well-tested, reliable, and CI/CD-ready.

##            ⚙️ Backend: Django REST E-Commerce API
A robust and feature-rich Django REST Framework API backend for e-commerce applications. This API provides all the essential functionalities needed to build a complete online shopping platform.

##              📋 Features
### 🔐 User Authentication & Authorization
JWT-based authentication

Registration, login, and token refresh

User profile management

Role-based access control (Admin/User)

###                📦 Product Management
Full product CRUD support

Product categories and filtering

Product image upload

Search functionality

### 🛒 Shopping Experience
Shopping cart with item management

Wishlist functionality

Ratings and reviews system

### 📑 Order Processing
Create, view, and track orders

Order history per user

Admin-controlled status updates

### 💳 Payment Integration
Secure transaction support

Multiple payment methods

Payment and order linkage

### 🛠️ Tech Stack
Django 4.2.7 – Python Web Framework

Django REST Framework 3.14.0 – API toolkit

JWT Authentication – Token-based user access

SQLite (default) – Configurable for PostgreSQL

Swagger/OpenAPI – Auto-generated API docs

### 📦 Dependencies
djangorestframework-simplejwt

django-cors-headers

psycopg2-binary

python-dotenv

## 🚀 Getting Started
- Prerequisites
- Python 3.8+
- pip
- Virtualenv (recommended)

Installation

 ``` git clone https://github.com/your-username/selectedtopicsproject.git ``` 
 
```cd PostMan```

``` python -m venv venv ```

``` source venv/bin/activate ```      # On Windows: venv\Scripts\activate

``` pip install -r ecommerce_api/requirements.txt
cd ecommerce_api
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver ```
## Access the API
Base URL: http://127.0.0.1:8000/api/

## 🧪 Automated Testing with Newman

This project includes automated API testing using Postman collections and Newman (Postman's command-line runner).

### Running Tests Locally

#### Prerequisites
- Node.js and npm installed
- Newman CLI (`npm install -g newman`)
- Newman HTML reporter (`npm install -g newman-reporter-htmlextra`)

#### Unix/Linux/macOS
```bash
# Make the script executable
chmod +x run_tests.sh

# Run the tests
./run_tests.sh
```

#### Windows
```cmd
# Run the tests
run_tests.bat
```
npm install -g newman
npm install -g newman-reporter-htmlextra
newman run postman_collection.json -e postman_environment.json -r htmlextra --reporter-htmlextra-export ./newman-report.html
### CI/CD Integration with GitHub Actions

This project includes GitHub Actions workflow that automatically runs the Postman tests on every push to the main branch and on pull requests.

The workflow:
1. Sets up the testing environment
2. Installs dependencies
3. Starts the Django server
4. Runs the Postman tests with Newman
5. Generates an HTML report
6. Uploads the report as an artifact

To view test results:
1. Go to the GitHub Actions tab in your repository
2. Click on the latest workflow run
3. Download the "newman-report" artifact to view the HTML test report

### Customizing Tests

To modify the tests:
1. Import the `postman_collection.json` file into Postman
2. Make your changes to the requests and tests
3. Export the updated collection and replace the existing file
4. Commit and push your changes

