from django.contrib.auth.models import User

def email_or_username_auth(identifier, password):
    # Try email login
    try:
        user = User.objects.get(email=identifier)
    except User.DoesNotExist:
        # Try username login
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            return None

    if user.check_password(password):
        return user

    return None
