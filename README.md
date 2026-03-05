# MENUL Backend

منصة MENUL هي نظام إدارة مطاعم ذكي مبني على Django + DRF، يغطّي:
- إدارة المستخدمين والصلاحيات حسب الدور.
- إدارة المطاعم والفروع والطاولات.
- إدارة المطابخ والقوائم والأصناف.
- إدارة جلسات الطلبات وعناصر الطلب مع تتبع الحالة.
- دعم طلب الضيف (بدون تسجيل دخول) عبر `session_password`.

---

## 1) هيكل المشروع

```text
backend/
  apps/
    authentication/   # تسجيل/دخول/خروج/كلمات مرور/تحقق
    accounts/         # إدارة المستخدمين (User CRUD + scope)
    restaurants/      # مطاعم + فروع + طاولات
    kitchens/         # المطابخ
    menu/             # التصنيفات + الأصناف
    orders/           # جلسات الطلب + عناصر الطلب + حالات الطلب
  menul/              # settings + urls
  scripts/
    seed_data.py      # تجهيز بيانات تجريبية مترابطة
```

---

## 2) المتطلبات

- Python 3.10+
- pip
- SQLite (افتراضي)

تثبيت الحزم:

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

---

## 3) التشغيل المحلي

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

السيرفر:
- `http://127.0.0.1:8000`

---

## 4) تجهيز بيانات تجريبية (Seed)

### الطريقة المباشرة
```bash
cd backend
python scripts/seed_data.py
```

### من داخل Django shell
```bash
cd backend
python manage.py shell
exec(open("scripts/seed_data.py").read())
```

**مخرجات السكربت**:
- ينشئ بيانات مترابطة: users/restaurants/branches/tables/kitchens/items/sessions/order-items.
- ينشئ سيناريوهات جاهزة للتجربة (جلسات مفتوحة ومغلقة + أصناف من أكثر من مطبخ).
- كلمة مرور جميع المستخدمين الافتراضية: `0000` (بيئة تطوير فقط).

---

## 5) أهم الـ API Endpoints

## Auth API
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `POST /api/auth/login/refresh/`
- `GET /api/auth/me/`
- `POST /api/auth/change-password/`
- `POST /api/auth/password-reset-request/`
- `POST /api/auth/password-reset-confirm/<uidb64>/<token>/`
- `GET /api/auth/verify-email/<uidb64>/<token>/`

## Accounts API
- `GET/POST /api/accounts/users/`
- `GET/PATCH/DELETE /api/accounts/users/<id>/`

## Restaurants API
- `GET/POST /api/restaurants/restaurants/`
- `GET/POST /api/restaurants/branches/`
- `GET/POST /api/restaurants/tables/`

## Kitchens API
- `GET/POST /api/kitchens/kitchens/`

## Menu API
- `GET/POST /api/menu/categories/`
- `GET/POST /api/menu/items/`

## Orders API
- `GET/POST /api/orders/sessions/`
- `GET/POST /api/orders/items/`

---

## 6) ملاحظات أمنية وتشغيلية

- النظام يعتمد JWT بشكل افتراضي للـ API.
- أدوار المطبخ (`chef`, `kitchen_manager`) عندهم صلاحيات مختلفة عن أدوار التشغيل الأمامي.
- الويتر يُقيّد حسب الفرع (أو فرع المطبخ إذا كان مربوطًا بمطبخ).
- إنشاء عنصر طلب كـ **ضيف** ممكن فقط عند تمرير `session_password` صحيح للجلسة الفعالة.

---

## 7) الاختبارات والفحوصات

```bash
cd backend
python manage.py check
python manage.py test -v 1
python manage.py test apps.orders.tests -v 1
```

