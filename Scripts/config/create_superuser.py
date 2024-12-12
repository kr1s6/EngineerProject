import os
import sys
import django
from django.contrib.auth import get_user_model

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ustawienie DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineerProject.settings')
django.setup()

User = get_user_model()

def create_superuser():
    username = "admin"
    email = "admin@example.com"
    password = "admin"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser created: {username}")
    else:
        print(f"Superuser {username} already exists.")

if __name__ == "__main__":
    create_superuser()
