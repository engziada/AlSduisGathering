# نظام تسجيل لقاء أسرة السديس

## مسارات النظام (Routes)

### مسارات التسجيل
- `/` (GET, POST) - الصفحة الرئيسية وبداية التسجيل
  - التحقق من وجود رقم الجوال في قائمة المدعوين
  - التحقق من عدم وجود تسجيل سابق
- `/register/<phone_number>` (GET, POST) - نموذج التسجيل
  - يتم التحقق من صلاحية رقم الجوال
  - التحقق من عدم وجود تسجيل سابق
  - إمكانية تسجيل الأطفال المصاحبين للنساء
- `/registered/<phone_number>` (POST, GET) - تأكيد التسجيل وعرض البيانات
  - عرض بيانات التسجيل
  - إمكانية تعديل أو حذف التسجيل
- `/delete/<phone_number>` (POST) - حذف التسجيل
  - حذف التسجيل وجميع الأطفال المرتبطين به
  - يتطلب تأكيد قبل الحذف
- `/convert_to_image` (POST) - تحويل البيانات إلى صورة

### مسارات لوحة التحكم (تتطلب تسجيل دخول المشرف)
- `/admin` (GET, POST) - لوحة تحكم المشرف
  - إدارة حالة التسجيل (مفتوح/مغلق)
  - عرض إحصائيات التسجيل
- `/delete_guest/<guest_phoneno>` (GET, POST) - حذف ضيف
- `/export` - تصدير البيانات إلى ملف Excel
  - تصدير بيانات المسجلين
  - تصدير بيانات الأطفال
- `/backup_db` - نسخ احتياطي لقاعدة البيانات
- `/upload/` (GET, POST) - رفع ملف
- `/restore_db` - استعادة قاعدة البيانات من النسخة الاحتياطية

### مسارات إدارة الجوائز (تتطلب تسجيل دخول المشرف)
- `/prizes` (GET, POST) - عرض قائمة الجوائز
- `/prizes/add` (GET, POST) - إضافة جائزة جديدة
- `/prizes/edit/<id>` (GET, POST) - تعديل جائزة
- `/prizes/delete/<id>` (POST) - حذف جائزة
- `/prizes/reset/<id>` (POST) - إعادة تعيين جائزة

### مسارات السحب على الجوائز (تتطلب تسجيل دخول المشرف)
- `/withdraw_prize` (GET, POST) - سحب الجوائز
- `/shuffle_numbers/<id>` (GET, POST) - خلط أرقام التسجيل
- `/confirm_prize/<prize_id>/<reg_no>` (GET, POST) - تأكيد الفائز بالجائزة

### مسارات تأكيد الحضور
- `/confirm_attendence` (GET, POST) - تأكيد الحضور

### مسارات البطاقات
- `/cards` - عرض البطاقات
- `/downloadcard1` (POST) - تحميل البطاقة الأولى
- `/downloadcard2` (POST) - تحميل البطاقة الثانية

## المميزات الرئيسية
- تسجيل الحضور مع البيانات الكاملة
- تسجيل الأطفال المصاحبين للنساء
- نظام سحب على الجوائز (للضيوف فقط)
- تصدير بيانات الضيوف والأطفال إلى Excel
- نظام نسخ احتياطي واستعادة
- إدارة كاملة للجوائز والسحوبات
- توليد وتحميل البطاقات
- نظام أمان متكامل للمشرفين
- التحقق المزدوج من صحة البيانات
- نظام تذاكر متكامل مع QR code للحضور
- خيارات متعددة لحفظ التذكرة (طباعة، PDF، صورة)

## Checkpoints
### Checkpoint 1 (2024-12-24)
- إضافة نظام التذاكر المتكامل
- دعم QR code لتأكيد الحضور
- إضافة خيارات حفظ التذكرة (طباعة، PDF، صورة)
- تحسين تصميم التذكرة وإضافة الشعار
- إضافة تصدير بيانات الأطفال في لوحة التحكم
- التأكد من عدم دخول الأطفال في نظام السحب على الجوائز

### Checkpoint 2 (2024-12-25)
- إزالة التحقق من جدول Google Spreadsheet للتسجيل المباشر
- تحديث تصميم تذكرة الحضور بالتواريخ والأوقات الجديدة
- تحسين تصميم الفوتر وإضافة شعار Z Solutions
- إضافة خاصية الفوتر المرن (يثبت في أسفل الشاشة عند قصر المحتوى)
- تحسين المظهر العام للتطبيق وإضافة هوامش متناسقة

### Checkpoint 3 (2024-12-25)
- إضافة نظام الصلاحيات المتعدد (مشرف ومستقبل)
- تقييد صلاحيات المستقبل لصفحة تأكيد الحضور فقط
- تحسين نظام تسجيل الدخول وإضافة أزرار تسجيل الخروج
- إضافة إحصائيات الأطفال في لوحة التحكم
- تحسين تنظيم الكود وإضافة التعليقات
- تحسين نظام الجلسات وإضافة الجلسات الدائمة

### Checkpoint 4 (2024-12-27)
- Fixed registration form to properly handle children registration for male guests
- Updated database schema to use gender-neutral terms (parent_phone instead of mother_phone)
- Added guest's full name display in attendance confirmation
- Improved mobile responsiveness:
  - Fixed logout button positioning on small screens
  - Made admin table horizontally scrollable while keeping page fixed
  - Optimized statistics display for mobile view

### Checkpoint 5 (2025-01-01)
- Fixed phone number handling in registration form
- Fixed children data inheritance for both male and female parents
- Made phone number readonly instead of disabled to ensure proper form submission
- For male parents: first child inherits father's name, grandfather's name, and family name from parent
- For female parents: first child only inherits emergency phone, subsequent children inherit names from first child
- Restricted male parents to only add male children
- Added proper validation and error handling for registration process

To revert to this checkpoint:
```bash
git checkout $(git rev-list -n 1 --before="2025-01-01 23:25:07" main)
```

## متطلبات النظام
- Python 3.8+
- Flask
- SQLAlchemy
- وباقي المتطلبات موجودة في ملف requirements.txt

## الميزات الأمنية
- حماية جميع مسارات المشرف بنظام تسجيل الدخول
- التحقق المزدوج من صحة رقم الجوال
- حماية عمليات الحذف والتعديل
- نظام النسخ الاحتياطي التلقائي
- التحقق من صحة البيانات قبل الإدخال
- حماية من هجمات CSRF
- تشفير جلسات المستخدم

## طريقة التشغيل
1. تثبيت المتطلبات: `pip install -r requirements.txt`
2. تحديث قاعدة البيانات: `python update_db.py`
3. تشغيل السيرفر: `python app.py`
4. فتح المتصفح على: `http://localhost:5000`

## طريقة النشر على Render.com
1. إنشاء حساب على Render.com
2. اختيار "New Web Service"
3. ربط المشروع من GitHub
4. تعيين Build Command: 
```bash
pip install -r requirements.txt && python update_db.py
```
5. تعيين Start Command: `python app.py`
6. اختيار Free Plan والضغط على Create Web Service

## ملاحظات هامة
- يجب التأكد من وجود مجلد `backup` لعمل النسخ الاحتياطي
- يجب التأكد من صلاحيات الوصول لقاعدة البيانات
- يتم تخزين سجلات النظام في مجلد `logs`
- يجب تعيين كلمة مرور المشرف قبل التشغيل