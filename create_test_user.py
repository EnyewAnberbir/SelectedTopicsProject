#!/usr/bin/env python
"""
Script to create a test user for API testing
Run with: python create_test_user.py
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

def create_test_user():
    User = get_user_model()
    
    # Create test user with known credentials
    email = 'test@example.com'
    password = 'testpass123'
    
    try:
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            print(f"✅ Test user '{email}' already exists")
            user = User.objects.get(email=email)
            # Update password to make sure it's correct
            user.set_password(password)
            user.save()
            print(f"🔄 Updated password for test user")
        else:
            # Create new test user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name='Test',
                last_name='User'
            )
            print(f"✅ Created test user '{email}' with password '{password}'")
        
        print(f"\n📋 Test User Details:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   First Name: {user.first_name}")
        print(f"   Last Name: {user.last_name}")
        print(f"   User ID: {user.id}")
        
        return user
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None

def create_test_data():
    """Create some test products and categories"""
    try:
        from products.models import Product, Category
        
        # Create test category
        category, created = Category.objects.get_or_create(
            name='Test Category',
            defaults={'description': 'Category for API testing'}
        )
        
        if created:
            print(f"✅ Created test category: {category.name}")
        else:
            print(f"✅ Test category already exists: {category.name}")
        
        # Create test products
        products_data = [
            {
                'name': 'Test Product 1',
                'description': 'First test product for API testing',
                'price': 29.99,
                'stock_quantity': 100
            },
            {
                'name': 'Test Product 2', 
                'description': 'Second test product for API testing',
                'price': 49.99,
                'stock_quantity': 50
            }
        ]
        
        created_products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    **product_data,
                    'category': category
                }
            )
            created_products.append(product)
            
            if created:
                print(f"✅ Created test product: {product.name}")
            else:
                print(f"✅ Test product already exists: {product.name}")
        
        return created_products
        
    except ImportError:
        print("⚠️  Products app not found, skipping test data creation")
        return []
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return []

if __name__ == '__main__':
    print("🚀 Setting up test data for API testing...\n")
    
    # Create test user
    user = create_test_user()
    
    if user:
        print("\n🛍️ Creating test products...")
        products = create_test_data()
        
        print(f"\n🎉 Test setup complete!")
        print(f"   • Created/verified test user")
        print(f"   • Created/verified {len(products)} test products")
        print(f"\n💡 You can now run your API tests:")
        print(f"   newman run postman_collection.json -e postman_environment.json")
    else:
        print("\n❌ Failed to create test user")
        sys.exit(1) 