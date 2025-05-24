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

+-------------------------+          +------------------------+          +-------------------------+
|         User            |          |        Product         |          |         Order           |
+-------------------------+          +------------------------+          +-------------------------+
| email: EmailField       |          | name: CharField        |          | order_number: CharField |
| first_name: CharField   |          | slug: SlugField        |          | order_status: CharField |
| last_name: CharField    |          | description: TextField |          | payment_status: CharField|
| phone_number: CharField |          | price: DecimalField    |          | shipping_cost: DecimalField|
| date_joined: DateTimeField|        | discount_price: DecimalField|     | total_price: DecimalField|
| is_active: BooleanField |          | stock: PositiveIntegerField|      | payment_method: CharField|
+-------------------------+          | is_available: BooleanField |      | payment_id: CharField   |
| full_name()             |<---------| is_featured: BooleanField |       | notes: TextField        |
+-------------------------+          +------------------------+          | tracking_number: CharField|
         |                           | get_discount_percent() |          +-------------------------+
         |                           | current_price()        |          | items_count()           |
         |                           +------------------------+          +-------------------------+
         |                                     |                                  |
         |                                     |                                  |
         v                                     v                                  v
+-------------------------+          +------------------------+          +-------------------------+
|        Address          |          |      ProductImage      |          |       OrderItem         |
+-------------------------+          +------------------------+          +-------------------------+
| address_type: CharField |          | image: ImageField      |          | product_name: CharField |
| street_address: CharField|         | is_primary: BooleanField|         | product_price: DecimalField|
| apartment_address: CharField|      +------------------------+          | quantity: PositiveIntegerField|
| city: CharField         |                    |                         | total_price: DecimalField|
| state: CharField        |                    |                         +-------------------------+
| country: CharField      |                    |
| postal_code: CharField  |                    |
| is_default: BooleanField|                    |
+-------------------------+                    |
         ^                                     |
         |                                     |
         |                                     v
+-------------------------+          +------------------------+          +-------------------------+
|         Cart            |          |        Review          |          |        Payment          |
+-------------------------+          +------------------------+          +-------------------------+
| created_at: DateTimeField|         | rating: PositiveSmallIntegerField| | payment_id: CharField   |
| updated_at: DateTimeField|         | comment: TextField     |          | amount: DecimalField    |
+-------------------------+          | created_at: DateTimeField|        | currency: CharField     |
| total_items()           |          | updated_at: DateTimeField|        | payment_method: CharField|
| total_price()           |          +------------------------+          | status: CharField       |
+-------------------------+                                              +-------------------------+
         |                                                                         |
         |                                                                         |
         v                                                                         v
+-------------------------+                                              +-------------------------+
|       CartItem          |                                              |         Refund          |
+-------------------------+                                              +-------------------------+
| quantity: PositiveIntegerField|                                        | amount: DecimalField    |
| created_at: DateTimeField|                                             | reason: TextField       |
| updated_at: DateTimeField|                                             | status: CharField       |
+-------------------------+                                              | refund_id: CharField    |
| total_price()           |                                              +-------------------------+
+-------------------------+

## Detailed User Flow Description

### Authentication Flow
1. **Register User**
   - POST `/api/auth/register/` - Create a new user account
   - Required fields: email, first_name, last_name, password

2. **Login**
   - POST `/api/auth/login/` - Authenticate and receive JWT tokens
   - Provides access_token and refresh_token

3. **Refresh Token**
   - POST `/api/auth/token/refresh/` - Get a new access token using refresh token

4. **User Profile**
   - GET `/api/auth/profile/` - View user profile information
   - PUT `/api/auth/profile/` - Update user profile information

### Admin Flows
1. **Category Management**
   - POST `/api/categories/` - Create new product category
   - PUT `/api/categories/{id}/` - Update existing category
   - DELETE `/api/categories/{id}/` - Remove a category

2. **Product Management**
   - POST `/api/products/` - Add new product
   - PUT `/api/products/{id}/` - Update existing product
   - DELETE `/api/products/{id}/` - Remove a product

3. **Dashboard**
   - GET `/api/dashboard/` - View dashboard summary

### User Flows
1. **List Categories**
   - GET `/api/categories/` - List all product categories

2. **List Products**
   - GET `/api/products/` - List all products

3. **Product Search**
   - GET `/api/products/?search=keyword` - Search for products

4. **Get Category**
   - GET `/api/categories/{id}/` - Get details of a specific category

5. **Get Product**
   - GET `/api/products/{id}/` - Get details of a specific product

6. **Filter Products**
   - GET `/api/products/?category=category_id&price=max_price` - Filter products by category and price

7. **Add Review**
   - POST `/api/reviews/` - Add a new review

8. **Update/Delete Review**
   - PUT `/api/reviews/{id}/` - Update an existing review
   - DELETE `/api/reviews/{id}/` - Remove a review

### Shopping Flow
1. **Get/View Cart**
   - GET `/api/carts/` - Get user's shopping cart

2. **Add Item to Cart**
   - POST `/api/carts/add/` - Add an item to the shopping cart

3. **Remove Item from Cart**
   - POST `/api/carts/remove/` - Remove an item from the shopping cart

4. **Clear Cart**
   - POST `/api/carts/clear/` - Clear the shopping cart

5. **Get Product**
   - GET `/api/products/{id}/` - Get details of a specific product

### Checkout Flow
1. **List/Create Address**
   - GET `/api/addresses/` - List user's addresses
   - POST `/api/addresses/` - Create a new address

2. **Set Default Address**
   - POST `/api/addresses/{id}/set_default/` - Set a specific address as default

3. **Create Order**
   - POST `/api/orders/` - Create a new order

4. **List Orders**
   - GET `/api/orders/` - List all orders

5. **Get Order**
   - GET `/api/orders/{id}/` - Get details of a specific order

6. **Request Refund**
   - POST `/api/refunds/` - Request a refund for an order

7. **Create/Process Payment**
   - POST `/api/payments/` - Create and process a payment

8. **List Orders**
   - GET `/api/orders/` - List all orders

9. **Create/Process Payment**
   - POST `/api/payments/` - Create and process a payment

