from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin")
else:
    u = User.objects.get(username="admin")
    u.set_password("admin")
    u.save()
print("Superuser 'admin' with password 'admin' is ready.")
