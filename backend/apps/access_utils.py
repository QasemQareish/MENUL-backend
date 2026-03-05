"""Utilities مشتركة للصلاحيات وربط المستخدمين بالنطاق التنظيمي."""

KITCHEN_ROLES = {"kitchen_manager", "chef"}


def is_kitchen_role(user) -> bool:
    """يتحقق إن المستخدم من فريق المطبخ (غير مسموح له بإدارة الطاولات/الجلسات)."""
    return getattr(user, "role", None) in KITCHEN_ROLES


def resolve_waiter_branch(user):
    """
    يحدد فرع الويتر الفعّال:
    1) إن كان مربوطًا بمطبخ -> فرع المطبخ.
    2) وإلا إن كان مربوطًا بفرع مباشر -> هذا الفرع.
    3) غير ذلك -> None.
    """
    if getattr(user, "kitchen_id", None):
        return user.kitchen.branch
    if getattr(user, "branch_id", None):
        return user.branch
    return None
