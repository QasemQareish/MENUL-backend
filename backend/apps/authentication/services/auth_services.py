from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import PermissionDenied

User = get_user_model()


def register_user(validated_data):
    email = validated_data.get("email")
    username = validated_data.get("username")
    password = validated_data.get("password")

    if User.objects.filter(email=email).exists():
        raise ValueError("Email already registered")
    if User.objects.filter(username=username).exists():
        raise ValueError("Username already taken")

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='owner',
        is_active=True,
    )
    return user


def login_user(username_or_email, password):
    try:
        user = User.objects.get(username=username_or_email)
    except User.DoesNotExist:
        try:
            user = User.objects.get(email=username_or_email)
        except User.DoesNotExist:
            raise ValueError("User not found")

    if not user.is_active:
        raise PermissionDenied("User account is inactive")

    if not check_password(password, user.password):
        raise ValueError("Invalid password")

    return user


def change_password(user, old_password, new_password):
    if not user.check_password(old_password):
        raise ValueError("Old password is incorrect")

    user.set_password(new_password)
    user.save()
    return user
