🛍️ E-Commerce API Testing & Automation with Postman
A feature-rich Django REST Framework backend for e-commerce and an automated Postman testing suite — combining backend API development and end-to-end API testing.

📌 Project Overview
This project showcases API testing and automation for a fully functional e-commerce backend built with Django REST Framework. Using Postman and Newman CLI, it ensures the API is well-tested, reliable, and CI/CD-ready.

⚙️ Backend: Django REST E-Commerce API
A robust and feature-rich Django REST Framework API backend for e-commerce applications. This API provides all the essential functionalities needed to build a complete online shopping platform.

📋 Features
🔐 User Authentication & Authorization
JWT-based authentication

Registration, login, and token refresh

User profile management

Role-based access control (Admin/User)

📦 Product Management
Full product CRUD support

Product categories and filtering

Product image upload

Search functionality

🛒 Shopping Experience
Shopping cart with item management

Wishlist functionality

Ratings and reviews system

📑 Order Processing
Create, view, and track orders

Order history per user

Admin-controlled status updates

💳 Payment Integration
Secure transaction support

Multiple payment methods

Payment and order linkage

🛠️ Tech Stack
Django 4.2.7 – Python Web Framework

Django REST Framework 3.14.0 – API toolkit

JWT Authentication – Token-based user access

SQLite (default) – Configurable for PostgreSQL

Swagger/OpenAPI – Auto-generated API docs

📦 Dependencies
djangorestframework-simplejwt

django-cors-headers

drf-yasg

Pillow

psycopg2-binary

python-dotenv

🚀 Getting Started
Prerequisites
Python 3.8+

pip

Virtualenv (recommended)

Installation
bash
Copy
Edit
git clone https://github.com/your-username/selectedtopicsproject.git
cd PostMan
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r ecommerce_api/requirements.txt
cd ecommerce_api
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Access the API
Base URL: http://127.0.0.1:8000/api/

