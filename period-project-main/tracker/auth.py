from django.contrib.auth.models import User

def email_or_username_auth(identifier, password):
    user = None
    if '@' in identifier:
        # User is trying to log in with an email
        try:
            # Get the first user with this email (in case there are duplicates, though signup should prevent it)
            user = User.objects.filter(email=identifier).first()
        except User.DoesNotExist:
            pass
    else:
        # User is trying to log in with a username
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            pass

    if user and user.check_password(password):
        return user

    return None
