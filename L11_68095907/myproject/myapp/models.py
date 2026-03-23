from django.db import models

# สร้างโมเดล Person
class Person(models.Model):
    name = models.CharField(max_length=100) # เก็บชื่อ ความยาวสูงสุด 100 ตัวอักษร
    age = models.IntegerField()             # เก็บอายุเป็นตัวเลขจำนวนเต็ม
    date = models.DateField(auto_now_add=True) # เก็บวันที่และบันทึกอัตโนมัติเมื่อเพิ่มข้อมูล

    # กำหนดให้แสดงชื่อและอายุเมื่อมีการเรียกดูอ็อบเจกต์ (เมธอดพิเศษ __str__)
    def __str__(self):
        return f"{self.name} - อายุ: {self.age}"