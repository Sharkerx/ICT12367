from django.apps import AppConfig


# ✅ แก้ชื่อ class ไม่ให้ชนกับ AppConfig ที่ import มา
class MyAppConfig(AppConfig):
    name = 'app'
    default_auto_field = 'django.db.models.BigAutoField'