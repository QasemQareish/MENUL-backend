from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from .models import OrderSession, OrderItem


@transaction.atomic
def create_session_if_not_exists(table):
    session = OrderSession.objects.select_for_update().filter(
        table=table,
        active=True
    ).first()

    if session:
        return session

    return OrderSession.objects.create(table=table)


def add_order_item(session, item, quantity, notes=""):
    if not session.active:
        raise PermissionDenied("الجلسة مغلقة")

    order_item = OrderItem.objects.create(
        order_session=session,
        item=item,
        quantity=quantity,
        price_at_order_time=item.price,
        notes=notes
    )

    session.total_amount += item.price * quantity
    session.save()

    return order_item


def update_order_status(user, order_item, new_status):
    role = getattr(user, 'role', None)

    transitions = {
        'pending': ['accepted', 'cancelled'],
        'accepted': ['cooking'],
        'cooking': ['ready'],
        'ready': ['served'],
    }

    if new_status not in transitions.get(order_item.status, []):
        raise PermissionDenied("تغيير حالة غير مسموح")

    order_item.status = new_status
    order_item.save()
    return order_item
