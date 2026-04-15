from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection

# ============================================================
# HELPER
# ============================================================
def admin_required(request):
    return bool(request.session.get('user_id'))

def customer_required(request):
    return bool(request.session.get('cus_logged_in'))

# ============================================================
# 🏠 0. PORTAL LANDING
# ============================================================
def portal_landing(request):
    if admin_required(request):
        return redirect('/dashboard/')
    if customer_required(request):
        return redirect('/browse/')
    return render(request, 'portal_login.html')

# ============================================================
# 🔐 1. ADMIN AUTH
# ============================================================
def login_view(request):
    if admin_required(request):
        return redirect('/dashboard/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT emp_id, emp_name 
                FROM employee 
                WHERE username=%s AND password=%s
            """, [username, password])
            user = cursor.fetchone()
        if user:
            request.session['user_id']   = user[0]
            request.session['user_name'] = user[1]
            return redirect('/dashboard/')
        return render(request, 'login.html', {'error': 'Username หรือ Password ไม่ถูกต้อง'})
    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    return redirect('/')

# ============================================================
# 🙋 2. CUSTOMER AUTH
# ============================================================
def register_view(request):
    """
    สมัครสมาชิก — EXEC sp_addcustomer_check
    ถ้าชื่อซ้ำ → ปฏิเสธ / ถ้าไม่ซ้ำ → INSERT ลูกค้าใหม่
    """
    if request.method == 'POST':
        cus_name = request.POST.get('cus_name', '').strip()
        phone    = request.POST.get('phone', '').strip()
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm  = request.POST.get('confirm', '').strip()

        if password != confirm:
            return render(request, 'customer_login.html', {'reg_error': 'รหัสผ่านไม่ตรงกัน'})
        if not all([cus_name, phone, email, password]):
            return render(request, 'customer_login.html', {'reg_error': 'กรุณากรอกข้อมูลให้ครบ'})

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM Customer WHERE email=%s", [email])
                if cursor.fetchone():
                    return render(request, 'customer_login.html',
                                  {'reg_error': 'Email นี้มีผู้ใช้งานแล้ว'})

                # EXEC sp_addcustomer_check — เช็คชื่อซ้ำ ถ้าไม่ซ้ำ INSERT
                cursor.execute(
                    "EXEC sp_addcustomer_check @cus_name=%s, @phone=%s, @email=%s",
                    [cus_name, phone, email]
                )

                cursor.execute(
                    "SELECT cus_id FROM Customer WHERE cus_name=%s AND email=%s",
                    [cus_name, email]
                )
                row = cursor.fetchone()
                if not row:
                    return render(request, 'customer_login.html',
                                  {'reg_error': '❌ ชื่อลูกค้าซ้ำ ไม่สามารถเพิ่มได้'})
                cus_id = int(row[0])

                cursor.execute(
                    "UPDATE Customer SET password=%s WHERE cus_id=%s",
                    [password, cus_id]
                )

            request.session['cus_logged_in'] = True
            request.session['cus_id']        = cus_id
            request.session['cus_name']      = cus_name
            return redirect('/browse/')

        except Exception as e:
            return render(request, 'customer_login.html',
                          {'reg_error': f'เกิดข้อผิดพลาด: {str(e)}'})

    return render(request, 'customer_login.html')

def customer_login_view(request):
    if customer_required(request):
        return redirect('/browse/')
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cus_id, cus_name FROM Customer
                WHERE email=%s AND password=%s
            """, [email, password])
            user = cursor.fetchone()
        if user:
            request.session['cus_logged_in'] = True
            request.session['cus_id']        = user[0]
            request.session['cus_name']      = user[1]
            return redirect('/browse/')
        return render(request, 'customer_login.html',
                      {'error': 'Email หรือรหัสผ่านไม่ถูกต้อง'})
    return render(request, 'customer_login.html')

def customer_logout_view(request):
    for key in ['cus_logged_in', 'cus_id', 'cus_name']:
        request.session.pop(key, None)
    return redirect('/')

# ============================================================
# 🏠 3. ADMIN DASHBOARD
# ============================================================
def dashboard(request):
    if not admin_required(request):
        return redirect('/login/')
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM Customer")
        total_customers = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Booking")
        total_bookings = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tourpackage")
        total_tours = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM employee")
        total_employee = cursor.fetchone()[0]
        # นับสลิปรอยืนยัน
        cursor.execute("SELECT COUNT(*) FROM payment WHERE status='pending'")
        pending_count = cursor.fetchone()[0]
    return render(request, 'Dashboard.html', {
        'total_customers': total_customers,
        'total_bookings':  total_bookings,
        'total_tours':     total_tours,
        'total_employee':  total_employee,
        'pending_count':   pending_count,
    })

# ============================================================
# 👥 4. ADMIN — CUSTOMERS
# ============================================================
def customer_list(request):
    if not admin_required(request):
        return redirect('/login/')
    keyword = request.GET.get('q', '')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.cus_id, c.cus_name, c.phone, c.email,
                   ISNULL(t.tour_name, '-'),
                   ISNULL(h.hotel_name, '-'),
                   ISNULL(e.emp_name, '-')
            FROM Customer c
            LEFT JOIN Booking b ON c.cus_id = b.cus_id
            LEFT JOIN Schedule s ON b.schedule_id = s.schedule_id
            LEFT JOIN tourpackage t ON s.tour_id = t.tour_id
            LEFT JOIN Hotel h ON s.hotel_id = h.hotel_id
            LEFT JOIN employee e ON b.emp_id = e.emp_id
            WHERE c.cus_name LIKE %s OR CAST(c.cus_id AS NVARCHAR) LIKE %s
            ORDER BY c.cus_id DESC
        """, [f'%{keyword}%', f'%{keyword}%'])
        rows = cursor.fetchall()
    data = [{'cus_id':r[0],'cus_name':r[1],'phone':r[2],'email':r[3],
             'tour_name':r[4],'hotel_name':r[5],'emp_name':r[6]} for r in rows]
    return render(request, 'customer.html', {'data': data})

def add_customer(request):
    """
    Admin เพิ่มลูกค้า:
    1. EXEC sp_addcustomer  → เบอร์ซ้ำ=UPDATE / ใหม่=INSERT
    2. EXEC sp_bookingtour  → ถ้าเลือก schedule จะจองให้ด้วย
       (Trigger trg_UpdateBookingCount → totalBooking +1 อัตโนมัติ)
    """
    if not admin_required(request):
        return redirect('/login/')

    if request.method == 'POST':
        cus_name    = request.POST.get('cus_name')
        phone       = request.POST.get('phone')
        email       = request.POST.get('email')
        schedule_id = request.POST.get('schedule_id')
        emp_id      = request.POST.get('emp_id') or '1'

        try:
            with connection.cursor() as cursor:
                # EXEC sp_addcustomer
                cursor.execute(
                    "EXEC sp_addcustomer @cus_name=%s, @phone=%s, @email=%s",
                    [cus_name, phone, email]
                )

                cursor.execute("SELECT cus_id FROM Customer WHERE phone=%s", [phone])
                row    = cursor.fetchone()
                cus_id = int(row[0]) if row else None

                # EXEC sp_bookingtour ถ้าเลือก schedule
                if cus_id and schedule_id and str(schedule_id).strip():
                    cursor.execute(
                        "EXEC sp_bookingtour @cus_id=%s, @schedule_id=%s, @emp_id=%s",
                        [cus_id, schedule_id, emp_id]
                    )

            return redirect('/customers/')

        except Exception as e:
            guides, schedules = _get_guides_schedules()
            return render(request, 'add.html', {
                'error': f'บันทึกไม่สำเร็จ: {str(e)}',
                'guides': guides, 'schedules': schedules
            })

    guides, schedules = _get_guides_schedules()
    return render(request, 'add.html', {'guides': guides, 'schedules': schedules})

def _get_guides_schedules():
    with connection.cursor() as cursor:
        cursor.execute("SELECT emp_id, emp_name FROM employee")
        guides = cursor.fetchall()
        cursor.execute("""
            SELECT s.schedule_id, s.tour_id, s.start_date, s.end_date, t.tour_name 
            FROM Schedule s JOIN tourpackage t ON s.tour_id = t.tour_id
            ORDER BY s.start_date DESC
        """)
        schedules = cursor.fetchall()
    return guides, schedules

def update_customer(request):
    if not admin_required(request):
        return redirect('/login/')
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE Customer SET cus_name=%s, phone=%s, email=%s WHERE cus_id=%s
            """, [request.POST.get('cus_name'), request.POST.get('phone'),
                  request.POST.get('email'), request.POST.get('cus_id')])
    return redirect('/customers/')

def delete_customer(request, id):
    if not admin_required(request):
        return redirect('/login/')
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM payment 
                WHERE booking_id IN (SELECT booking_id FROM Booking WHERE cus_id=%s)
            """, [id])
            cursor.execute("DELETE FROM Booking WHERE cus_id=%s", [id])
            cursor.execute("DELETE FROM Customer WHERE cus_id=%s", [id])
        return redirect('/customers/')
    except Exception as e:
        return HttpResponse(f'เกิดข้อผิดพลาด: {str(e)}')

# ============================================================
# 📦 5. ADMIN — BOOKINGS
# ============================================================
def booking_list(request):
    if not admin_required(request):
        return redirect('/login/')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.booking_id, c.cus_name, t.tour_name,
                   s.start_date, s.end_date,
                   ISNULL(e.emp_name,'No Guide'), b.status, h.hotel_name
            FROM Booking b
            JOIN Customer c ON b.cus_id = c.cus_id
            JOIN Schedule s ON b.schedule_id = s.schedule_id
            JOIN tourpackage t ON s.tour_id = t.tour_id
            LEFT JOIN Hotel h ON s.hotel_id = h.hotel_id
            LEFT JOIN employee e ON b.emp_id = e.emp_id
            ORDER BY b.booking_id DESC
        """)
        rows = cursor.fetchall()
    data = [{'booking_id':r[0],'cus_name':r[1],'tour_name':r[2],
             'start':r[3],'end':r[4],'guide':r[5],'status':r[6],'hotel_name':r[7]}
            for r in rows]
    return render(request, 'booking.html', {'data': data})

# ============================================================
# 🗺️ 6. ADMIN — TOURS
# ============================================================
def tour_list(request):
    """
    Admin ดูทัวร์:
    - dbo.fn_totalprice(tour_id)        → ราคารวม VAT 7%
    - dbo.fn_countcustomer(schedule_id) → จำนวนคนจองในแต่ละรอบ
    """
    if not admin_required(request):
        return redirect('/login/')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tour_id, tour_name, price, image,
                   dbo.fn_totalprice(tour_id) AS price_vat
            FROM tourpackage
            ORDER BY tour_id
        """)
        tours = cursor.fetchall()

        cursor.execute("SELECT cus_id, cus_name FROM Customer ORDER BY cus_name")
        customers = cursor.fetchall()

        cursor.execute("SELECT emp_id, emp_name FROM employee")
        guides = cursor.fetchall()

        cursor.execute("""
            SELECT s.schedule_id, s.tour_id, s.start_date, s.end_date,
                   t.tour_name,
                   dbo.fn_countcustomer(s.schedule_id) AS booked_count
            FROM Schedule s
            JOIN tourpackage t ON s.tour_id = t.tour_id
            ORDER BY s.start_date
        """)
        schedules = cursor.fetchall()

    data = [{'tour_id':t[0],'tour_name':t[1],'price':t[2],
             'image':t[3],'price_vat':t[4]} for t in tours]
    schedule_data = [{'schedule_id':s[0],'tour_id':s[1],'start_date':s[2],
                      'end_date':s[3],'tour_name':s[4],'booked_count':s[5]}
                     for s in schedules]
    return render(request, 'tour.html', {
        'data': data, 'customers': customers,
        'guides': guides, 'schedules': schedule_data
    })

# ============================================================
# 👔 7. ADMIN — EMPLOYEE
# ============================================================
def employee_list(request):
    if not admin_required(request):
        return redirect('/login/')
    with connection.cursor() as cursor:
        cursor.execute("SELECT emp_id, emp_name, role, username FROM employee")
        rows = cursor.fetchall()
    data = [{'emp_id':r[0],'emp_name':r[1],'role':r[2],'username':r[3]} for r in rows]
    return render(request, 'employee.html', {'data': data})

# ============================================================
# 🏨 8. ADMIN — HOTELS
# ============================================================
def hotel_list(request):
    if not admin_required(request):
        return redirect('/login/')
    with connection.cursor() as cursor:
        cursor.execute("SELECT hotel_id, hotel_name, location, price FROM Hotel")
        hotels = cursor.fetchall()
    data = []
    for h in hotels:
        hotel_id, hotel_name, location, price = h
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.booking_id, c.cus_name, c.phone,
                       t.tour_name, s.start_date, s.end_date, b.status
                FROM Booking b
                JOIN Customer c ON b.cus_id = c.cus_id
                JOIN Schedule s ON b.schedule_id = s.schedule_id
                JOIN tourpackage t ON s.tour_id = t.tour_id
                WHERE s.hotel_id = %s
                ORDER BY s.start_date DESC
            """, [hotel_id])
            rows = cursor.fetchall()
        guests = [{'booking_id':r[0],'cus_name':r[1],'phone':r[2],
                   'tour_name':r[3],'start_date':r[4],'end_date':r[5],'status':r[6]}
                  for r in rows]
        data.append({'id':hotel_id,'name':hotel_name,'location':location,
                     'price':price,'guests':guests})
    return render(request, 'hotel.html', {'data': data})

# ============================================================
# 💳 9. ADMIN — PAYMENT
# ============================================================
def payment_page(request):
    if not admin_required(request):
        return redirect('/login/')
    if request.method == 'POST':
        cus_id      = request.POST.get('cus_id')
        schedule_id = request.POST.get('schedule_id')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.cus_name, t.tour_name, s.start_date, s.end_date,
                       t.price,
                       dbo.fn_totalprice(t.tour_id) AS price_vat,
                       ISNULL(h.hotel_name, '-') AS hotel_name
                FROM Schedule s
                JOIN tourpackage t ON s.tour_id = t.tour_id
                JOIN Customer c ON c.cus_id = %s
                LEFT JOIN Hotel h ON s.hotel_id = h.hotel_id
                WHERE s.schedule_id = %s
            """, [cus_id, schedule_id])
            row = cursor.fetchone()
        if row is None:
            return render(request, 'payment.html',
                          {'error': 'ไม่พบข้อมูลการเดินทาง', 'data': None})
        data = {
            'cus_name':    row[0],
            'tour_name':   row[1],
            'start':       row[2],
            'end':         row[3],
            'price':       row[4],
            'price_vat':   row[5],
            'hotel_name':  row[6],
            'cus_id':      cus_id,
            'schedule_id': schedule_id
        }
        return render(request, 'payment.html', {'data': data})
    return redirect('/tours/')

def confirm_payment(request):
    """
    Admin ยืนยันชำระเงิน:
    1. EXEC sp_bookingtour → จองทัวร์
       (Trigger trg_UpdateBookingCount → totalBooking +1 อัตโนมัติ)
    2. INSERT payment
    """
    if not admin_required(request):
        return redirect('/login/')
    if request.method != 'POST':
        return redirect('/tours/')

    cus_id      = request.POST.get('cus_id')
    schedule_id = request.POST.get('schedule_id')
    method      = request.POST.get('method', 'โอนเงิน')
    emp_id      = request.POST.get('emp_id', '1')

    try:
        with connection.cursor() as cursor:
            # EXEC sp_bookingtour
            cursor.execute(
                "EXEC sp_bookingtour @cus_id=%s, @schedule_id=%s, @emp_id=%s",
                [cus_id, schedule_id, emp_id]
            )

            cursor.execute("""
                SELECT MAX(booking_id) FROM Booking
                WHERE cus_id=%s AND schedule_id=%s
            """, [cus_id, schedule_id])
            row = cursor.fetchone()
            if not row or row[0] is None:
                return render(request, 'payment.html',
                              {'error': 'ไม่สามารถสร้างการจองได้', 'data': None})
            booking_id = int(row[0])

            cursor.execute("""
                SELECT t.price FROM Schedule s
                JOIN tourpackage t ON s.tour_id = t.tour_id
                WHERE s.schedule_id=%s
            """, [schedule_id])
            ar     = cursor.fetchone()
            amount = ar[0] if ar else 0

            cursor.execute("SELECT ISNULL(MAX(payment_id),0)+1 FROM payment")
            payment_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO payment (payment_id, booking_id, amount, method, status)
                VALUES (%s,%s,%s,%s,'paid')
            """, [payment_id, booking_id, amount, method])

        return redirect('/bookings/')
    except Exception as e:
        return render(request, 'payment.html',
                      {'error': f'เกิดข้อผิดพลาด: {str(e)}', 'data': None})

# ============================================================
# 🌐 10. CUSTOMER PORTAL
# ============================================================
def customer_home(request):
    """
    หน้าแรก Customer:
    - dbo.fn_totalprice(tour_id) → ราคารวม VAT 7%
    """
    if not customer_required(request):
        return redirect('/customer-login/')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TOP 6
                tour_id, tour_name, price, image,
                dbo.fn_totalprice(tour_id) AS price_vat
            FROM tourpackage
            ORDER BY tour_id
        """)
        featured = cursor.fetchall()
    tours = [{'tour_id':t[0],'tour_name':t[1],'price':t[2],
              'image':t[3],'price_vat':t[4]} for t in featured]
    return render(request, 'customer_home.html', {
        'tours':    tours,
        'cus_name': request.session.get('cus_name', '')
    })

def customer_tours(request):
    """
    หน้าทัวร์ Customer:
    - dbo.fn_totalprice(tour_id)        → ราคารวม VAT 7%
    - dbo.fn_countcustomer(schedule_id) → จำนวนคนจองในแต่ละรอบ
    """
    if not customer_required(request):
        return redirect('/customer-login/')
    keyword = request.GET.get('q', '')
    with connection.cursor() as cursor:
        if keyword:
            cursor.execute("""
                SELECT tour_id, tour_name, price, image,
                       dbo.fn_totalprice(tour_id) AS price_vat
                FROM tourpackage
                WHERE tour_name LIKE %s
                ORDER BY tour_id
            """, [f'%{keyword}%'])
        else:
            cursor.execute("""
                SELECT tour_id, tour_name, price, image,
                       dbo.fn_totalprice(tour_id) AS price_vat
                FROM tourpackage
                ORDER BY tour_id
            """)
        tours = cursor.fetchall()

        cursor.execute("""
            SELECT s.schedule_id, s.tour_id, s.start_date, s.end_date,
                   t.tour_name,
                   ISNULL(h.hotel_name, '-') AS hotel_name,
                   DATEDIFF(day, s.start_date, s.end_date) AS nights,
                   dbo.fn_countcustomer(s.schedule_id) AS booked_count
            FROM Schedule s
            JOIN tourpackage t ON s.tour_id = t.tour_id
            LEFT JOIN Hotel h ON s.hotel_id = h.hotel_id
            WHERE s.start_date >= CAST(GETDATE() AS DATE)
            ORDER BY s.tour_id, s.start_date
        """)
        schedules = cursor.fetchall()

    tour_data = [{'tour_id':t[0],'tour_name':t[1],'price':t[2],
                  'image':t[3],'price_vat':t[4]} for t in tours]
    schedule_data = [{'schedule_id':s[0],'tour_id':s[1],'start_date':s[2],
                      'end_date':s[3],'tour_name':s[4],'hotel_name':s[5],
                      'nights':s[6],'booked_count':s[7]} for s in schedules]
    return render(request, 'customer_tours.html', {
        'tours':     tour_data,
        'schedules': schedule_data,
        'keyword':   keyword,
        'cus_name':  request.session.get('cus_name', '')
    })

def customer_hotels(request):
    if not customer_required(request):
        return redirect('/customer-login/')
    with connection.cursor() as cursor:
        cursor.execute("SELECT hotel_id, hotel_name, location, price, image FROM Hotel")
        hotels = cursor.fetchall()
    data = [{'hotel_id':h[0],'hotel_name':h[1],'location':h[2],
             'price':h[3],'image':h[4] if h[4] else ''} for h in hotels]
    return render(request, 'customer_hotels.html', {
        'hotels':   data,
        'cus_name': request.session.get('cus_name', '')
    })

def customer_payment_page(request):
    """
    หน้าชำระเงิน Customer:
    - dbo.fn_totalprice(tour_id) → ราคารวม VAT 7%
    - Auto-assign ไกด์จากจังหวัดในชื่อทัวร์อัตโนมัติ
      เช่น "ทัวร์ภูเก็ต" → หาไกด์ที่ชื่อมีคำว่า "ภูเก็ต" หรือ KEYWORD ที่ match
    """
    if not customer_required(request):
        return redirect('/customer-login/')
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        cus_id      = request.session.get('cus_id')

        # Mapping คำในชื่อทัวร์ → จังหวัด (keyword สำหรับ match กับ emp_name)
        PROVINCE_KEYWORDS = {
            'ภูเก็ต':    'ภูเก็ต',
            'เชียงใหม่': 'เชียงใหม่',
            'กระบี่':    'กระบี่',
            'พัทยา':     'พัทยา',
            'หัวหิน':    'หัวหิน',
            'เขาใหญ่':   'เขาใหญ่',
            'อยุธยา':    'อยุธยา',
            'เชียงราย':  'เชียงราย',
            'โขง':       'โขง',
            'แม่ฮ่องสอน':'แม่ฮ่องสอน',
            'ระยอง':     'ระยอง',
            'ลำปาง':     'ลำปาง',
        }

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT t.tour_name, s.start_date, s.end_date,
                       t.price,
                       dbo.fn_totalprice(t.tour_id) AS price_vat,
                       ISNULL(h.hotel_name, '-') AS hotel_name,
                       c.cus_name,
                       DATEDIFF(day, s.start_date, s.end_date) AS nights,
                       s.guide_id, t.tour_id
                FROM Schedule s
                JOIN tourpackage t ON s.tour_id = t.tour_id
                LEFT JOIN Hotel h ON s.hotel_id = h.hotel_id
                JOIN Customer c ON c.cus_id = %s
                WHERE s.schedule_id = %s
            """, [cus_id, schedule_id])
            row = cursor.fetchone()

        if row is None:
            return render(request, 'customer_payment.html',
                          {'error': 'ไม่พบข้อมูล', 'data': None})

        tour_name = row[0]
        guide_id  = row[8]
        guide_name = '-'
        emp_id_auto = None

        # Auto-assign ไกด์จากจังหวัดในชื่อทัวร์
        with connection.cursor() as cursor:
            if guide_id:
                # ถ้า schedule มี guide_id อยู่แล้ว ใช้คนนั้นเลย
                cursor.execute(
                    "SELECT emp_id, emp_name FROM employee WHERE emp_id=%s",
                    [guide_id]
                )
                g = cursor.fetchone()
                if g:
                    emp_id_auto = g[0]
                    guide_name  = g[1]
            else:
                # หาจังหวัดจากชื่อทัวร์ แล้ว match กับ emp_name
                matched_kw = None
                for kw in PROVINCE_KEYWORDS:
                    if kw in tour_name:
                        matched_kw = PROVINCE_KEYWORDS[kw]
                        break

                if matched_kw:
                    cursor.execute("""
                        SELECT TOP 1 emp_id, emp_name
                        FROM employee
                        WHERE emp_name LIKE %s
                        ORDER BY emp_id
                    """, [f'%{matched_kw}%'])
                else:
                    # ถ้า match ไม่ได้ → หาไกด์ที่ว่างอยู่ (จองน้อยที่สุด)
                    cursor.execute("""
                        SELECT TOP 1 e.emp_id, e.emp_name
                        FROM employee e
                        LEFT JOIN Booking b ON b.emp_id = e.emp_id
                        GROUP BY e.emp_id, e.emp_name
                        ORDER BY COUNT(b.booking_id) ASC
                    """)

                g = cursor.fetchone()
                if g:
                    emp_id_auto = g[0]
                    guide_name  = g[1]

        data = {
            'tour_name':    row[0],
            'start':        row[1],
            'end':          row[2],
            'price':        row[3],
            'price_vat':    row[4],
            'hotel_name':   row[5],
            'cus_name':     row[6],
            'nights':       row[7],
            'guide_name':   guide_name,
            'emp_id':       emp_id_auto,
            'schedule_id':  schedule_id,
            'cus_id':       cus_id
        }
        return render(request, 'customer_payment.html', {'data': data})
    return redirect('/browse/tours/')

def customer_confirm_payment(request):
    """
    Customer ยืนยันชำระเงิน:
    1. EXEC sp_bookingtour → จองทัวร์
    2. INSERT payment (status=pending ถ้าโอนเงิน / paid ถ้าบัตร/เงินสด)
    3. ถ้าโอนเงิน → บันทึกสลิป → รอ Admin verify
    4. INSERT Ticket
    5. Redirect → ticket page
    """
    if not customer_required(request):
        return redirect('/customer-login/')
    if request.method != 'POST':
        return redirect('/browse/tours/')

    cus_id      = request.POST.get('cus_id')
    schedule_id = request.POST.get('schedule_id')
    method      = request.POST.get('method', 'โอนเงิน')
    emp_id      = request.POST.get('emp_id') or '1'
    slip_file   = request.FILES.get('slip_file')

    # โอนเงิน = pending จนกว่าจะ verify สลิป
    # บัตรเครดิต / เงินสด = paid ทันที
    payment_status = 'pending' if method == 'โอนเงิน' else 'paid'

    try:
        import os, uuid
        from django.conf import settings

        # บันทึกไฟล์สลิป
        slip_path = None
        if slip_file and method == 'โอนเงิน':
            ext       = os.path.splitext(slip_file.name)[1]
            filename  = f"slip_{uuid.uuid4().hex}{ext}"
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'slips')
            os.makedirs(upload_dir, exist_ok=True)
            full_path = os.path.join(upload_dir, filename)
            with open(full_path, 'wb+') as f:
                for chunk in slip_file.chunks():
                    f.write(chunk)
            slip_path = f'slips/{filename}'

        with connection.cursor() as cursor:
            # 1. EXEC sp_bookingtour
            cursor.execute(
                "EXEC sp_bookingtour @cus_id=%s, @schedule_id=%s, @emp_id=%s",
                [cus_id, schedule_id, emp_id]
            )

            # 2. ดึง booking_id ที่เพิ่งสร้าง
            cursor.execute("""
                SELECT MAX(booking_id) FROM Booking
                WHERE cus_id=%s AND schedule_id=%s
            """, [cus_id, schedule_id])
            row = cursor.fetchone()
            if not row or row[0] is None:
                return redirect('/browse/my-bookings/')
            booking_id = int(row[0])

            # 3. ดึงราคาทัวร์
            cursor.execute("""
                SELECT dbo.fn_totalprice(t.tour_id)
                FROM Schedule s
                JOIN tourpackage t ON s.tour_id = t.tour_id
                WHERE s.schedule_id=%s
            """, [schedule_id])
            ar     = cursor.fetchone()
            amount = ar[0] if ar else 0

            # 4. INSERT payment พร้อม slip_path
            cursor.execute("SELECT ISNULL(MAX(payment_id),0)+1 FROM payment")
            payment_id = cursor.fetchone()[0]

            if slip_path:
                cursor.execute("""
                    INSERT INTO payment (payment_id, booking_id, amount, method, status, slip_path)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, [payment_id, booking_id, amount, method, payment_status, slip_path])
            else:
                cursor.execute("""
                    INSERT INTO payment (payment_id, booking_id, amount, method, status)
                    VALUES (%s,%s,%s,%s,%s)
                """, [payment_id, booking_id, amount, method, payment_status])

            # 5. INSERT Ticket (สร้างตั๋วเมื่อจองสำเร็จ)
            qr_ref = f"TPR{booking_id:05d}"
            cursor.execute("""
                INSERT INTO Ticket (booking_id, qr_ref, status, slip_path)
                VALUES (%s, %s, 'active', %s)
            """, [booking_id, qr_ref, slip_path])

        # ถ้าโอนเงิน → ไปหน้ารอยืนยัน / ถ้าจ่ายทันที → ไปตั๋ว
        if payment_status == 'pending':
            return redirect(f'/browse/pending/{booking_id}/')
        return redirect(f'/browse/ticket/{booking_id}/')

    except Exception as e:
        return render(request, 'customer_payment.html', {
            'error': f'เกิดข้อผิดพลาด: {str(e)}', 'data': None
        })


def payment_pending_view(request, booking_id):
    """หน้ารอยืนยันสลิป — แสดงหลังอัปโหลดสลิปโอนเงิน"""
    if not customer_required(request):
        return redirect('/customer-login/')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.booking_id, t.tour_name, s.start_date, s.end_date,
                   c.cus_name, p.amount, p.slip_path, p.status
            FROM Booking b
            JOIN Schedule s    ON b.schedule_id = s.schedule_id
            JOIN tourpackage t ON s.tour_id = t.tour_id
            JOIN Customer c    ON b.cus_id = c.cus_id
            LEFT JOIN payment p ON p.booking_id = b.booking_id
            WHERE b.booking_id = %s
        """, [booking_id])
        row = cursor.fetchone()
    if not row:
        return redirect('/browse/my-bookings/')
    data = {
        'booking_id': row[0], 'tour_name': row[1],
        'start': row[2],      'end': row[3],
        'cus_name': row[4],   'amount': row[5],
        'slip_path': row[6],  'status': row[7],
    }
    return render(request, 'payment_pending.html', {
        'data': data, 'cus_name': request.session.get('cus_name', '')
    })


def admin_verify_payment(request, payment_id):
    """Admin ยืนยันสลิป → เปลี่ยน status เป็น paid"""
    if not admin_required(request):
        return redirect('/login/')
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE payment
            SET status='paid', verified_at=GETDATE()
            WHERE payment_id=%s
        """, [payment_id])
        # ดึง booking_id
        cursor.execute("SELECT booking_id FROM payment WHERE payment_id=%s", [payment_id])
        row = cursor.fetchone()
    if row:
        return redirect(f'/browse/ticket/{row[0]}/')
    return redirect('/bookings/')

def ticket_view(request, booking_id):
    """หน้าตั๋วยืนยันการจอง — ปริ้นได้"""
    if not customer_required(request):
        return redirect('/customer-login/')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.booking_id, c.cus_name, c.phone, c.email,
                   t.tour_name, s.start_date, s.end_date,
                   ISNULL(h.hotel_name, '-'),
                   ISNULL(e.emp_name, '-'),
                   ISNULL(p.amount, 0),
                   ISNULL(p.method, '-'),
                   p.payment_date,
                   DATEDIFF(day, s.start_date, s.end_date),
                   ISNULL(e.province, '-')
            FROM Booking b
            JOIN Customer c     ON b.cus_id      = c.cus_id
            JOIN Schedule s     ON b.schedule_id = s.schedule_id
            JOIN tourpackage t  ON s.tour_id      = t.tour_id
            LEFT JOIN Hotel h   ON s.hotel_id     = h.hotel_id
            LEFT JOIN employee e ON b.emp_id      = e.emp_id
            LEFT JOIN payment p  ON p.booking_id  = b.booking_id
            WHERE b.booking_id = %s
        """, [booking_id])
        row = cursor.fetchone()
    if not row:
        return redirect('/browse/my-bookings/')
    ticket = {
        'booking_id':   row[0],
        'cus_name':     row[1],
        'phone':        row[2],
        'email':        row[3],
        'tour_name':    row[4],
        'start':        row[5],
        'end':          row[6],
        'hotel_name':   row[7],
        'guide_name':   row[8],
        'amount':       row[9],
        'method':       row[10],
        'payment_date': row[11],
        'nights':       row[12],
        'province':     row[13],
        'price_vat':    float(row[9]) if row[9] else 0,
    }
    return render(request, 'ticket.html', {
        'ticket':   ticket,
        'cus_name': request.session.get('cus_name', '')
    })

def my_bookings(request):
    if not customer_required(request):
        return redirect('/customer-login/')
    cus_id = request.session.get('cus_id')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.booking_id, t.tour_name, s.start_date, s.end_date,
                   b.status,
                   ISNULL(h.hotel_name, '-'),
                   ISNULL(p.amount, 0),
                   ISNULL(p.method, '-')
            FROM Booking b
            JOIN Schedule s ON b.schedule_id = s.schedule_id
            JOIN tourpackage t ON s.tour_id = t.tour_id
            LEFT JOIN Hotel h ON s.hotel_id = h.hotel_id
            LEFT JOIN payment p ON p.booking_id = b.booking_id
            WHERE b.cus_id = %s
            ORDER BY b.booking_id DESC
        """, [cus_id])
        rows = cursor.fetchall()
    data = [{'booking_id':r[0],'tour_name':r[1],'start':r[2],'end':r[3],
             'status':r[4] or '-','hotel_name':r[5],
             'amount':r[6],'method':r[7]} for r in rows]
    return render(request, 'my_bookings.html', {
        'data':     data,
        'cus_name': request.session.get('cus_name', '')
    })

def book_hotel(request):
    if not customer_required(request):
        return redirect('/customer-login/')
    if request.method == 'POST':
        hotel_id = request.POST.get('hotel_id')
        checkin  = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        cus_id   = request.session.get('cus_id')
        if cus_id:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO HotelBooking (cus_id, hotel_id, checkin_date, checkout_date, status)
                    VALUES (%s,%s,%s,%s,'Booked')
                """, [cus_id, hotel_id, checkin, checkout])
    return redirect('/browse/my-bookings/')

def portal_view(request):
    return render(request, 'portal_login.html')


# ============================================================
# 🧾 ADMIN — ตรวจสอบสลิป
# ============================================================
def admin_slip_list(request):
    """Admin ดูรายการสลิปที่รอยืนยัน"""
    if not admin_required(request):
        return redirect('/login/')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.payment_id, p.booking_id, p.amount, p.method,
                   p.slip_path, p.status,
                   c.cus_name, t.tour_name
            FROM payment p
            JOIN Booking b    ON p.booking_id = b.booking_id
            JOIN Customer c   ON b.cus_id     = c.cus_id
            JOIN Schedule s   ON b.schedule_id = s.schedule_id
            JOIN tourpackage t ON s.tour_id    = t.tour_id
            WHERE p.status = 'pending'
            ORDER BY p.payment_id DESC
        """)
        rows = cursor.fetchall()
    pending = [{'payment_id':r[0],'booking_id':r[1],'amount':r[2],
                'method':r[3],'slip_path':r[4],'status':r[5],
                'cus_name':r[6],'tour_name':r[7]} for r in rows]
    return render(request, 'verify_slips.html', {'pending_payments': pending})


def admin_verify_payment(request, payment_id):
    """Admin ยืนยันสลิป → status = paid → สร้างตั๋ว"""
    if not admin_required(request):
        return redirect('/login/')
    with connection.cursor() as cursor:
        # อัปเดต payment → paid
        cursor.execute("""
            UPDATE payment
            SET status='paid', verified_at=GETDATE()
            WHERE payment_id=%s
        """, [payment_id])

        # ดึง booking_id
        cursor.execute("SELECT booking_id FROM payment WHERE payment_id=%s", [payment_id])
        row = cursor.fetchone()
        if not row:
            return redirect('/admin/slips/')
        booking_id = row[0]

        # อัปเดต Booking status → Confirmed
        cursor.execute("""
            UPDATE Booking SET status='Confirmed'
            WHERE booking_id=%s
        """, [booking_id])

        # เช็คว่ามี Ticket แล้วหรือยัง ถ้ายังไม่มีให้สร้าง
        cursor.execute("SELECT 1 FROM Ticket WHERE booking_id=%s", [booking_id])
        if not cursor.fetchone():
            qr_ref = f"TPR{booking_id:05d}"
            cursor.execute("""
                INSERT INTO Ticket (booking_id, qr_ref, status)
                VALUES (%s, %s, 'active')
            """, [booking_id, qr_ref])

    return redirect('/admin/slips/')


def admin_reject_payment(request, payment_id):
    """Admin ปฏิเสธสลิป → status = rejected"""
    if not admin_required(request):
        return redirect('/login/')
    with connection.cursor() as cursor:
        # ดึง booking_id ก่อน
        cursor.execute("SELECT booking_id FROM payment WHERE payment_id=%s", [payment_id])
        row = cursor.fetchone()

        cursor.execute("""
            UPDATE payment SET status='rejected'
            WHERE payment_id=%s
        """, [payment_id])

        if row:
            cursor.execute("""
                UPDATE Booking SET status='Cancelled'
                WHERE booking_id=%s
            """, [row[0]])

            cursor.execute("""
                UPDATE Ticket SET status='cancelled'
                WHERE booking_id=%s
            """, [row[0]])

    return redirect('/admin/slips/')