from django.db import models

# 🔥 ใช้ VIEW
class ViewCustomer(models.Model):
    CusID = models.CharField(max_length=10, primary_key=True)
    Cusname = models.CharField(max_length=50)
    RegisYear = models.IntegerField()
    EmpID = models.CharField(max_length=10)
    EMPName = models.CharField(max_length=50)

    class Meta:
        db_table = 'viewCustomer'
        managed = False


class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    cus_id = models.IntegerField()
    schedule_id = models.IntegerField()

    class Meta:
        db_table = 'Booking'
        managed = False
class Employee(models.Model):
    emp_id = models.CharField(max_length=10, primary_key=True)
    emp_name = models.CharField(max_length=50)
    role = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)

    class Meta:
        db_table = 'employee'
        managed = False

class TourPackage(models.Model):
    tour_id = models.AutoField(primary_key=True)
    tour_name = models.CharField(max_length=100)
    price = models.FloatField()
    image = models.URLField(max_length=500, null=True, blank=True)  # ← เพิ่มบรรทัดนี้

    class Meta:
        db_table = 'tourpackage'
        managed = False