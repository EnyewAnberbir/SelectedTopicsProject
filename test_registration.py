#!/usr/bin/env python
"""
Test script to verify registration error handling
"""
import os
import sys
import django

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

def test_duplicate_email_registration():
    """Test that registering with duplicate email returns proper error"""
    client = APIClient()
    
    # First, create a user
    user_data = {
        'email': 'test@example.com',
        'password': 'testpassword123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    # Create the first user successfully
    response = client.post('/api/auth/register/', user_data, format='json')
    print(f"First registration response status: {response.status_code}")
    print(f"First registration response data: {response.data}")
    
    # Try to register with the same email again
    duplicate_user_data = {
        'email': 'test@example.com',  # Same email
        'password': 'anotherpassword123',
        'first_name': 'Another',
        'last_name': 'User'
    }
    
    response = client.post('/api/auth/register/', duplicate_user_data, format='json')
    print(f"Duplicate registration response status: {response.status_code}")
    print(f"Duplicate registration response data: {response.data}")
    
    # Clean up
    User.objects.filter(email='test@example.com').delete()
    
    if response.status_code == 400:
        print("✅ SUCCESS: Duplicate email registration properly returns 400 Bad Request")
        if 'email' in response.data and 'already exists' in str(response.data['email']):
            print("✅ SUCCESS: Error message correctly indicates email already exists")
        else:
            print("❌ FAIL: Error message doesn't properly indicate email already exists")
    else:
        print(f"❌ FAIL: Expected 400 status code, got {response.status_code}")

if __name__ == '__main__':
    test_duplicate_email_registration() 