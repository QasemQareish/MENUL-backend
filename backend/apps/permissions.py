from rest_framework import permissions

class RoleBasedPermission(permissions.BasePermission):
    """
    Hierarchical permissions system:
    - Owner: all entities in restaurant
    - Branch Manager: all entities in branch
    - Kitchen Manager: all entities in kitchen
    - Chef: only manage order items (accept/cancel)
    - Waiter: full control of tables in branch + orders
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Superadmin/Admin: كل شيء
        if user.role in ['superadmin','admin']:
            return True

        # Owner: كل شيء ضمن مطعمه
        if user.role == 'owner':
            if hasattr(obj, 'restaurant'):
                return obj.restaurant == user.restaurant
            if hasattr(obj, 'branch'):
                return obj.branch.restaurant == user.restaurant
            if hasattr(obj, 'kitchen'):
                return obj.kitchen.branch.restaurant == user.restaurant
            if hasattr(obj, 'table'):
                return obj.table.branch.restaurant == user.restaurant
            if hasattr(obj, 'branch_manager') or hasattr(obj, 'kitchen_manager') or hasattr(obj, 'waiter'):
                return obj.branch.restaurant == user.restaurant
            return False

        # Branch Manager: كل شيء ضمن فرعه
        if user.role == 'branch_manager':
            if hasattr(obj, 'branch'):
                return obj.branch == user.branch
            if hasattr(obj, 'kitchen'):
                return obj.kitchen.branch == user.branch
            if hasattr(obj, 'table'):
                return obj.table.branch == user.branch
            if hasattr(obj, 'order_session'):
                return obj.order_session.table.branch == user.branch
            return False

        # Kitchen Manager: كل شيء ضمن مطبخه
        if user.role == 'kitchen_manager':
            if hasattr(obj, 'kitchen'):
                return obj.kitchen == user.kitchen
            if hasattr(obj, 'order_item'):
                return obj.order_item.item.kitchen == user.kitchen
            return False

        # Chef: فقط إدارة OrderItems (قبول/رفض/إلغاء)
        if user.role == 'chef':
            if hasattr(obj, 'order_item'):
                return obj.order_item.item.kitchen == user.kitchen
            return False

        # Waiter: كل الطاولات ضمن الفرع + إدارة الطلبات
        if user.role == 'waiter':
            if hasattr(obj, 'table'):
                return obj.table.branch == user.branch
            if hasattr(obj, 'order_session'):
                return obj.order_session.table.branch == user.branch
            if hasattr(obj, 'order_item'):
                return obj.order_item.order_session.table.branch == user.branch
            return False

        return False
