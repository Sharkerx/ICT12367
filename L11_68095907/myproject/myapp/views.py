from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Person 

def index(request):
    # ดึงข้อมูลประชากรทั้งหมดมาแสดงในหน้าแรก
    persons = Person.objects.all() 
    return render(request, "index.html", {'persons': persons})

def about(request):
    return HttpResponse("<h1>เกี่ยวกับเรา</h1>")

def form(request):
    # ตรวจสอบว่าเป็นการส่งข้อมูลมาจากฟอร์มหรือไม่ (POST)
    if request.method == "POST":
        # รับข้อมูลจากฟอร์ม
        name = request.POST.get("name")
        age = request.POST.get("age")
        
        # บันทึกข้อมูลลงฐานข้อมูล
        Person.objects.create(
            name=name,
            age=age
        )
        
        # บันทึกเสร็จแล้วให้เปลี่ยนเส้นทางไปหน้าแรก
        return redirect("/")
    else:
        # หากเป็นการเข้าหน้าเว็บปกติ ให้แสดงหน้าฟอร์ม
        return render(request, 'form.html') 

def contact(request):
    return HttpResponse("<h1>68095907 วรัญญู แก้วเมือง</h1>")