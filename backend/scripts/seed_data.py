import os
import sys
from pathlib import Path
from decimal import Decimal

import django
from django.db import transaction
from django.utils import timezone

# أضف مجلد backend إلى PYTHONPATH حتى تعمل الاستيرادات دائمًا
# ملاحظة: عند التشغيل عبر exec داخل manage.py shell لا يكون __file__ متاحًا.
if "__file__" in globals():
    SCRIPT_PATH = Path(__file__).resolve()
else:
    SCRIPT_PATH = (Path.cwd() / "scripts" / "seed_data.py").resolve()

BACKEND_DIR = SCRIPT_PATH.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# مهم: اسم مشروع الإعدادات الصحيح هو menul وليس MENUL
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "menul.settings")
django.setup()
from apps.accounts.models import User
from apps.kitchens.models import Kitchen
from apps.menu.models import Category, Item
from apps.orders.models import OrderSession, OrderItem
from apps.restaurants.models import Restaurant, Branch, Table

DEFAULT_PASSWORD = "0000"


def create_or_update_user(username: str, role: str, email: str, **links) -> User:
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={"email": email, "role": role, "is_active": True},
    )
    user.email = email
    user.role = role
    user.is_active = True

    # روابط اختيارية (restaurant/branch/kitchen)
    user.restaurant = links.get("restaurant")
    user.branch = links.get("branch")
    user.kitchen = links.get("kitchen")

    user.set_password(DEFAULT_PASSWORD)
    user.save()
    return user


@transaction.atomic
def seed():
    print("🚀 بدء إنشاء بيانات تجريبية مترابطة...")

    # 1) مستخدمي النظام الأساسيين
    superadmin = create_or_update_user("superadmin_user", "superadmin", "superadmin@example.com")
    admin = create_or_update_user("admin_user", "admin", "admin@example.com")

    # 2) ملاك المطاعم
    owner_1 = create_or_update_user("owner_user_1", "owner", "owner1@example.com")
    owner_2 = create_or_update_user("owner_user_2", "owner", "owner2@example.com")

    # 3) مطعمين
    restaurant_1, _ = Restaurant.objects.get_or_create(name="Test Restaurant 1", defaults={"owner": owner_1})
    restaurant_2, _ = Restaurant.objects.get_or_create(name="Test Restaurant 2", defaults={"owner": owner_2})

    restaurant_1.owner = owner_1
    restaurant_2.owner = owner_2
    restaurant_1.save()
    restaurant_2.save()

    # ربط الملاك بمطاعمهم (عبر FK في User)
    owner_1.restaurant = restaurant_1
    owner_1.save(update_fields=["restaurant"])
    owner_2.restaurant = restaurant_2
    owner_2.save(update_fields=["restaurant"])

    # 4) الفروع
    branches = []
    for restaurant in [restaurant_1, restaurant_2]:
        for idx in [1, 2]:
            branch, _ = Branch.objects.get_or_create(
                restaurant=restaurant,
                branch_number=idx,
                defaults={
                    "name": f"{restaurant.name} - Branch {idx}",
                    "location": f"Location {idx}",
                    "is_active": True,
                },
            )
            branch.name = f"{restaurant.name} - Branch {idx}"
            branch.location = f"Location {idx}"
            branch.is_active = True
            branch.save()
            branches.append(branch)

    # 5) الطاولات
    tables = []
    for branch in branches:
        for number, seats in [(1, 2), (2, 4), (3, 6)]:
            table, _ = Table.objects.get_or_create(
                branch=branch,
                number=number,
                defaults={"seats": seats},
            )
            table.seats = seats
            table.save()
            tables.append(table)

    # 6) المطابخ + التصنيفات + الأصناف
    kitchens = []
    all_items = []
    for branch in branches:
        for kitchen_idx in [1, 2]:
            kitchen, _ = Kitchen.objects.get_or_create(name=f"Kitchen {kitchen_idx}", branch=branch)
            kitchens.append(kitchen)

            for cat_idx in [1, 2]:
                category, _ = Category.objects.get_or_create(name=f"Category {cat_idx}", kitchen=kitchen)
                for item_idx, price in [(1, Decimal("10.00")), (2, Decimal("20.00")), (3, Decimal("30.00"))]:
                    item, _ = Item.objects.get_or_create(
                        name=f"{kitchen.name} - Item {item_idx}",
                        category=category,
                        defaults={"price": price, "available": True, "kitchen": kitchen},
                    )
                    item.price = price
                    item.available = True
                    item.kitchen = kitchen
                    item.save()
                    all_items.append(item)

    # 7) مستخدمو التشغيل لكل فرع/مطبخ
    role_users = {
        "superadmin": superadmin,
        "admin": admin,
    }

    for branch in branches:
        restaurant = branch.restaurant

        # Branch manager
        bm = create_or_update_user(
            username=f"branch_manager_b{branch.id}",
            role="branch_manager",
            email=f"branch_manager_b{branch.id}@example.com",
            restaurant=restaurant,
            branch=branch,
        )
        role_users[bm.username] = bm

        # Waiter مربوط بالفرع
        waiter_branch = create_or_update_user(
            username=f"waiter_branch_b{branch.id}",
            role="waiter",
            email=f"waiter_branch_b{branch.id}@example.com",
            restaurant=restaurant,
            branch=branch,
        )
        role_users[waiter_branch.username] = waiter_branch

        # Waiter مربوط بمطبخ (بدون branch مباشر)
        branch_kitchen = Kitchen.objects.filter(branch=branch).first()
        waiter_kitchen = create_or_update_user(
            username=f"waiter_kitchen_b{branch.id}",
            role="waiter",
            email=f"waiter_kitchen_b{branch.id}@example.com",
            restaurant=restaurant,
            kitchen=branch_kitchen,
        )
        role_users[waiter_kitchen.username] = waiter_kitchen

        # Kitchen manager + chef لكل مطبخ
        for kitchen in Kitchen.objects.filter(branch=branch):
            km = create_or_update_user(
                username=f"kitchen_manager_k{kitchen.id}",
                role="kitchen_manager",
                email=f"kitchen_manager_k{kitchen.id}@example.com",
                restaurant=restaurant,
                branch=branch,
                kitchen=kitchen,
            )
            chef = create_or_update_user(
                username=f"chef_k{kitchen.id}",
                role="chef",
                email=f"chef_k{kitchen.id}@example.com",
                restaurant=restaurant,
                branch=branch,
                kitchen=kitchen,
            )
            role_users[km.username] = km
            role_users[chef.username] = chef

    # 8) العملاء
    customers = []
    for i in [1, 2, 3, 4]:
        customer = create_or_update_user(
            username=f"customer_{i}",
            role="customer",
            email=f"customer_{i}@example.com",
        )
        customers.append(customer)
        role_users[customer.username] = customer

    # 9) جلسات الطلب + عناصر الطلب
    # سننشئ جلسة فعّالة لكل فرع على الطاولة 1، ونغلق جلسة الطاولة 2 للتجربة.
    for idx, branch in enumerate(branches):
        branch_tables = Table.objects.filter(branch=branch).order_by("number")
        table_active = branch_tables.first()
        table_closed = branch_tables.filter(number=2).first()
        customer = customers[idx % len(customers)]

        # جلسة فعّالة
        active_session, _ = OrderSession.objects.get_or_create(
            table=table_active,
            active=True,
            defaults={"customer": customer, "payment_status": "unpaid"},
        )
        active_session.customer = customer
        active_session.payment_status = "unpaid"
        active_session.save()

        # ربط عناصر من مطبخين مختلفين بنفس الجلسة (إذا توفر)
        kitchens_in_branch = list(Kitchen.objects.filter(branch=branch).order_by("id"))
        if kitchens_in_branch:
            for kitchen_idx, kitchen in enumerate(kitchens_in_branch[:2]):
                item = Item.objects.filter(kitchen=kitchen).order_by("id").first()
                if not item:
                    continue

                qty = kitchen_idx + 1
                order_item, _ = OrderItem.objects.get_or_create(
                    order_session=active_session,
                    item=item,
                    defaults={
                        "quantity": qty,
                        "price_at_order_time": item.price,
                        "notes": f"auto-seeded from {kitchen.name}",
                        "status": "pending",
                    },
                )
                order_item.quantity = qty
                order_item.price_at_order_time = item.price
                order_item.notes = f"auto-seeded from {kitchen.name}"
                order_item.status = "pending"
                order_item.save()

        # إعادة حساب total_amount للجلسة
        total = Decimal("0.00")
        for oi in active_session.order_items.all():
            total += oi.price_at_order_time * oi.quantity
        active_session.total_amount = total
        active_session.save(update_fields=["total_amount"])

        # جلسة مغلقة للتجربة
        if table_closed:
            closed_session, _ = OrderSession.objects.get_or_create(
                table=table_closed,
                active=False,
                defaults={
                    "customer": customer,
                    "payment_status": "paid",
                    "opened_at": timezone.now(),
                    "closed_at": timezone.now(),
                },
            )
            closed_session.customer = customer
            closed_session.active = False
            closed_session.payment_status = "paid"
            if not closed_session.closed_at:
                closed_session.closed_at = timezone.now()
            closed_session.save()

    # 10) فحوصات سريعة للتأكد من الترابط
    assert Restaurant.objects.count() >= 2, "فشل إنشاء المطاعم"
    assert Branch.objects.count() >= 4, "فشل إنشاء الفروع"
    assert Table.objects.count() >= 12, "فشل إنشاء الطاولات"
    assert Kitchen.objects.count() >= 8, "فشل إنشاء المطابخ"
    assert User.objects.filter(role="waiter").exists(), "فشل إنشاء الويتر"
    assert OrderSession.objects.exists(), "فشل إنشاء الجلسات"
    assert OrderItem.objects.exists(), "فشل إنشاء عناصر الطلب"

    print("✅ تم إنشاء البيانات بنجاح.")
    print(f"- المستخدمين: {User.objects.count()}")
    print(f"- المطاعم: {Restaurant.objects.count()}")
    print(f"- الفروع: {Branch.objects.count()}")
    print(f"- الطاولات: {Table.objects.count()}")
    print(f"- المطابخ: {Kitchen.objects.count()}")
    print(f"- الأصناف: {Item.objects.count()}")
    print(f"- الجلسات: {OrderSession.objects.count()}")
    print(f"- عناصر الطلب: {OrderItem.objects.count()}")
    print("🔐 كلمة المرور الافتراضية لجميع المستخدمين: 0000")


if __name__ in {"__main__", "__console__", "django.core.management.commands.shell"} or "__file__" not in globals():
    seed()
