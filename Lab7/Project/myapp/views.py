from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("ICT12367 SPU</h1>")

def about(request):
    return HttpResponse("<h1>เกี่ยวกับเรา</H1>")

def form(request):
    return render(request, 'form.html')

def contact(request):
    return HttpResponse('ติดต่อ ข้อมูลนักศึกษา 68095907 นาย วรัญญู แก้วเมือง')