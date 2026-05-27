import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def verify_login_redirect():
    client = Client()
    username = 'testuser'
    password = 'Start123!'
    
    # Ensure user exists
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(username=username, password=password)

    # Login
    response = client.post('/accounts/login/', {'username': username, 'password': password}, follow=True)
    
    # Verify Redirect
    if response.redirect_chain:
        print(f"Redirected to: {response.redirect_chain[-1][0]}")
        # Check if redirected to home '/'
        if response.redirect_chain[-1][0] == '/':
             print("PASS: Redirected to Home")
        else:
             print(f"FAIL: Redirected to {response.redirect_chain[-1][0]}")
    else:
        print(f"FAIL: No redirect. Status: {response.status_code}")

if __name__ == '__main__':
    verify_login_redirect()
