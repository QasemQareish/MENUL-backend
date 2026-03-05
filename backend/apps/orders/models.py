from django.db import models
from django.utils import timezone
from django.db.models import Q
import uuid
import random
import string


def generate_6_digit():
    return ''.join(random.choices(string.digits, k=6))


class OrderSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    table = models.ForeignKey(
        'restaurants.Table',
        on_delete=models.CASCADE,
        related_name='order_sessions'
    )

    customer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_sessions'
    )

    active = models.BooleanField(default=True)

    session_password = models.CharField(max_length=6, default=generate_6_digit)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('unpaid', 'Unpaid'),
            ('paid', 'Paid'),
        ],
        default='unpaid'
    )

    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def close(self):
        self.active = False
        self.closed_at = timezone.now()
        self.save()

        self.table.current_session_password = generate_6_digit()
        self.table.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['table'],
                condition=Q(active=True),
                name='unique_active_session_per_table'
            )
        ]

    def __str__(self):
        return f"Session {self.id} - Table {self.table.number}"


class OrderItem(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('cooking', 'Cooking'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('cancelled', 'Cancelled'),
    ]

    order_session = models.ForeignKey(
        OrderSession,
        on_delete=models.CASCADE,
        related_name='order_items'
    )

    item = models.ForeignKey(
        'menu.Item',
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    price_at_order_time = models.DecimalField(max_digits=10, decimal_places=2)

    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_customer_edit(self):
        return self.order_session.active and self.status == 'pending'

    def __str__(self):
        return f"{self.item.name} x{self.quantity}"
