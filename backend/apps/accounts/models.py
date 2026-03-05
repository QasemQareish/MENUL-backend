from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, role='customer', **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        email = self.normalize_email(email)

        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered")

        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, role='superadmin', **extra_fields)


# -------------------- User Model --------------------
class User(AbstractUser):
    # قيم role محفوظة في قاعدة البيانات، والاسم الثاني هو الوصف الظاهر للمستخدم.
    ROLE_CHOICES = [
        ("superadmin", "مدير النظام العام"),
        ("admin", "مشرف النظام"),
        ("owner", "مالك المطعم"),
        ("branch_manager", "مدير الفرع"),
        ("kitchen_manager", "مدير المطبخ"),
        ("chef", "الطاهي"),
        ("waiter", "النادل"),
        ("customer", "الزبون"),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # العلاقات
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )
    branch = models.ForeignKey(
        "restaurants.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )
    kitchen = models.ForeignKey(
        "kitchens.Kitchen",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "role"]

    def __str__(self):
        return f"{self.username} ({self.role})"
