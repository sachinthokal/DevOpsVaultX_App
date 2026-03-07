import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devopsvaultx.settings')
django.setup()

User = get_user_model()

# .env मधून सर्व डिटेल्स घेणे
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'devopsvaultx')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'support@devopsvaultx.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'devopsvaultx@1799')
first_name = os.getenv('DJANGO_SUPERUSER_FIRST_NAME', 'DevOps')
last_name = os.getenv('DJANGO_SUPERUSER_LAST_NAME', 'VaultX')

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser: {username}")
    User.objects.create_superuser(
        username=username, 
        email=email, 
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    print("Superuser created successfully!")
else:
    # जर तुम्हाला एक्झिस्टिंग युजरचे नाव अपडेट करायचे असेल तर:
    user = User.objects.get(username=username)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    print(f"Superuser {username} already exists. Names updated.")