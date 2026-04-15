 TravelPro — Premium Travel Management System

# ✈️ TravelPro — Premium Travel Management System

**ระบบจัดการบริษัททัวร์และการจองแบบครบวงจร** *(Full-Stack Web Application with Admin & Customer Portal)*

---

## 📋 ภาพรวมระบบ (System Overview)

TravelPro เป็นระบบบริหารจัดการทัวร์และการจองที่ถูกออกแบบประสบการณ์ผู้ใช้ (UX/UI) ใหม่ทั้งหมด โดยเน้นความทันสมัย ความชัดเจน และการใช้งานจริงของทั้งฝั่งแอดมินและลูกค้า

ระบบครอบคลุมตั้งแต่หน้า **Portal Landing** ไปจนถึงกระบวนการออก **E-Ticket** ที่พร้อมพิมพ์ พร้อม **Dashboard** สรุปข้อมูลการจอง และระบบ **ตรวจสอบสลิปโอนเงิน** โดย Admin แบบ Real-time

---

## 🛠️ เทคโนโลยีและเครื่องมือที่ใช้ (Tech Stack & Tools)

| ส่วนของระบบ | เทคโนโลยีและการนำไปใช้งาน |
|---|---|
| **Back-end Server** | Python 3.12 + Django 6.0 (Views, Routing, Session Auth) |
| **Database** | Microsoft SQL Server (เชื่อมต่อผ่าน `mssql` + ODBC Driver 18, `Trusted_Connection`) |
| **Front-end Design** | HTML5 + CSS3 + Bootstrap Icons (Django Template เรนเดอร์ UI ตรงๆ) |
| **Interactivity** | Vanilla JavaScript (Confirm Dialog, Dynamic UI) |
| **Icons & Fonts** | Bootstrap Icons 1.11, Google Fonts (Playfair Display, Cormorant Garamond) |
| **UI Components** | SweetAlert-style Confirm ผ่าน `onclick="return confirm(...)"` |
| **Media Storage** | Django Media Files (`MEDIA_ROOT`) สำหรับเก็บสลิปโอนเงิน |

---

## ✨ เค้าโครงสีหลักของแบรนด์ (Brand Theme)

- **Deep Navy** (`#0A1628`, `#101F3A`): สีหลักพื้นหลัง แสดงความหรูหราและเป็นมืออาชีพ
- **Gold** (`#C9A84C`, `#E8C97A`): สีแอคเซ็นท์สำคัญ ปุ่ม CTA และตัวเลขหลัก
- **Emerald Green** (`#059669`, `#34D399`): สีแสดงสถานะ Confirmed และการกระทำสำเร็จ
- **Crimson Red** (`#DC2626`, `#F87171`): สีแสดงสถานะ Cancelled และการลบ
- **Amber** (`#D97706`, `#FCD34D`): สีแสดงสถานะ Pending รอการยืนยัน

---

## 📖 คู่มือการใช้งานระบบ (User Manual)

### 1. หน้า Portal Landing ( `/` )

- หน้าแรกของระบบ แสดงปุ่มเลือก **Admin** หรือ **Customer**
- ถ้า Login อยู่แล้วจะ Redirect ไปหน้าที่เหมาะสมอัตโนมัติ

### 2. แดชบอร์ดสำหรับแอดมิน ( `/dashboard/` )

- **KPI Stats**: ตัวเลขรวมด้านบน 4 การ์ด (Total Customers, Total Bookings, Tour Packages, Employees) ดึงข้อมูลสดจากฐานข้อมูล
- **Quick Actions**: ลิงก์ไปยังฟังก์ชันที่ใช้บ่อย เช่น Add Customer, View Bookings, Manage Tours
- **Navigation Sidebar**: เมนูด้านซ้ายเข้าถึงทุกส่วนของระบบ Admin

### 3. ระบบ E-Ticket และการปริ้นท์ ( `/browse/ticket/<id>/` )

- เข้าดู E-Ticket ได้หลังจากชำระเงินสำเร็จและ Admin ยืนยันสลิปแล้ว
- ตัวประกอบด้วย: รายละเอียดลูกค้า, ชื่อทัวร์, วันเดินทาง, โรงแรม, ไกด์, ยอดชำระ, QR Reference
- **วิธีพิมพ์**: กดปุ่ม Print จากเบราว์เซอร์ — ระบบจะแสดงข้อมูลในรูปแบบที่เหมาะสำหรับการพิมพ์
- สถานะ **Cancelled** จะไม่สามารถปริ้นตั๋วได้ (ปุ่มตั๋วถูกซ่อน)

### 4. ตารางข้อมูลและการจัดการ ( `/customers/`, `/bookings/`, `/tours/` เป็นต้น )

- แต่ละตารางฐานข้อมูลจะแสดงผลในรูปแบบตารางสะอาดตา
- มีสไตล์สลับสีแถว เพื่ออ่านข้อมูลแนวยาวง่ายขึ้น
- **Action Buttons**: ปุ่ม Edit และ Delete พร้อม `confirm dialog` ก่อนลบเสมอ
- **Status Badge**: สีเปลี่ยนตาม Status — เขียว = Confirmed, แดง = Cancelled, เหลือง = Pending

### 5. ระบบตรวจสอบสลิป ( `/admin/slips/` )

- Admin ดูรายการสลิปที่ลูกค้าอัปโหลดทั้งหมดในรูปแบบ Card
- แต่ละ Card แสดง: ชื่อลูกค้า, ชื่อทัวร์, ยอดเงิน, วิธีชำระ, รูปภาพสลิป
- **ยืนยัน**: เปลี่ยน Payment status → `paid`, Booking status → `Confirmed`, Ticket status → `active`
- **ปฏิเสธ**: เปลี่ยน Payment status → `rejected`, Booking status → `Cancelled`, Ticket status → `cancelled`

### 6. ระบบจองทัวร์ของลูกค้า ( `/browse/tours/` )

- ลูกค้าเลือกแพ็กเกจทัวร์ ดูวันเดินทาง โรงแรม และราคา
- กด **จองเลย** → เลือกวิธีชำระเงิน → อัปโหลดสลิป (กรณีโอนเงิน)
- หลังจองจะ Redirect ไปหน้า **รอยืนยัน** `/browse/pending/<id>/` หรือ **ตั๋ว** `/browse/ticket/<id>/` ทันที

### 7. ประวัติการจองของลูกค้า ( `/browse/my-bookings/` )

- แสดงรายการจองทั้งหมดพร้อม Status Badge สีชัดเจน
- **Confirmed** = มีปุ่มปริ้นตั๋ว 🖨️
- **Cancelled** = แสดงข้อความ "ยกเลิกแล้ว" ไม่มีปุ่มตั๋ว
- **Pending** = แสดงข้อความ "รอยืนยัน" ไม่มีปุ่มตั๋ว

---

## 🔑 บัญชีสำหรับการทดสอบระบบ (Test Credentials)

สำหรับการเข้าสู่ระบบในฐานะแอดมินหรือผู้ดูแลระบบ:

| ระดับผู้เข้าใช้งาน | Username | Password |
|---|---|---|
| 👑 **Administrator** (ผู้ดูแลระบบ) | admin | admin |
| 🧳 **Customer** (ลูกค้าตัวอย่าง) | pati@example.com | (ตามที่สมัคร) |

> **หมายเหตุ**: หากไม่สามารถเข้าถึงได้ ให้ตรวจสอบข้อมูลใน SQL Server Management Studio โดยตรง

---

## ⚙️ ขั้นตอนการติดตั้งและตั้งค่าระบบ (Installation Guide)

เพื่อให้ระบบทำงานได้อย่างสมบูรณ์ทั้งในส่วนของ Backend (Django) และฐานข้อมูล (SQL Server) กรุณาทำตามขั้นตอนอย่างละเอียดดังนี้:

### 📦 สิ่งที่ต้องติดตั้งไว้ในเครื่องก่อน (Prerequisites)

1. **Python 3.12** หรือใหม่กว่า
2. **Microsoft SQL Server** (เวอร์ชัน Express ก็ใช้งานได้) พร้อมโปรแกรม **SSMS** (SQL Server Management Studio)
3. **ODBC Driver 18 for SQL Server** (จำเป็นสำหรับให้ Python เชื่อมต่อ Database ได้)
4. **Git** บนเดสก์ท็อป

---

### Step 1: ดาวน์โหลดโปรเจกต์

ดึงซอร์สโค้ดล่าสุดจากฐานเก็บข้อมูลลงมายังเครื่องของคุณ

```bash
git clone https://github.com/<your-username>/travelpro.git
cd travelpro
cd myproject
```

---

### Step 2: สร้างอ้อมกอดเสมือน (Virtual Environment)

เพื่อไม่ให้ไลบรารีของโปรเจกต์นี้ไปตีกับโปรเจกต์อื่น กรุณาสร้าง venv และติดตั้ง dependencies:

```bash
# สร้าง Environment ชื่อ venv
python -m venv venv

# Activate Environment (สำหรับ Windows)
venv\Scripts\activate

# หากใช้ Mac/Linux ให้ใช้:
# source venv/bin/activate

# ติดตั้งแพคเกจที่จำเป็น
pip install django mssql-django
```

---

### Step 3: เตรียมฐานข้อมูล (Database Setup)

ระบบใช้ **SQL Server** และเชื่อมต่อผ่าน **Windows Authentication (Trusted Connection)**

1. เปิดโปรแกรม **SQL Server Management Studio (SSMS)**
2. ล็อคอินเข้าสู่ Server ของคุณ
3. สร้างฐานข้อมูลชื่อ **`Tour operator`**
4. รัน SQL Script เพื่อสร้างตารางทั้งหมด:

```sql
-- ตัวอย่างโครงสร้างตารางหลัก
CREATE TABLE Customer (
    cus_id   INT PRIMARY KEY IDENTITY,
    cus_name NVARCHAR(100),
    phone    NVARCHAR(20),
    email    NVARCHAR(100),
    password NVARCHAR(100)
);
-- ... (ดูไฟล์ SQL เต็มในโฟลเดอร์ database/)
```

---

### Step 4: ตั้งค่าการเชื่อมต่อ Django เข้ากับ SQL Server

เปิดไฟล์ `myproject/myproject/settings.py` แล้วแก้ไขส่วน `DATABASES` ให้ตรงกับ SQL Server ของคุณ:

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'Tour operator',       # ชื่อฐานข้อมูล
        'USER': '',                     # ปล่อยว่างถ้าใช้ Windows Auth
        'PASSWORD': '',
        'HOST': r'YOUR_PC_NAME\SQLEXPRESS',  # ← เปลี่ยนเป็นชื่อเครื่องของคุณ
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;Trusted_Connection=yes;'
        },
    }
}
```

> **วิธีหาชื่อ Server Name**: เปิด SSMS → ดูชื่อที่ช่อง "Server name" ตอน Login เช่น `DESKTOP-XXXXX\SQLEXPRESS`

---

### Step 5: สร้างโฟลเดอร์ Media

ระบบจะเก็บไฟล์สลิปโอนเงินที่ลูกค้าอัปโหลดในโฟลเดอร์นี้:

```bash
mkdir myproject/media
mkdir myproject/media/slips
```

---

### Step 6: ทดสอบเปิดเซิร์ฟเวอร์ (Run Local Server)

```bash
cd myproject
python manage.py runserver
```

> 🎉 **ยินดีด้วย!** ระบบพร้อมใช้งานแล้ว เปิดเบราว์เซอร์ของคุณแล้วไปที่:
>
> - **หน้าหลัก / Portal**: http://127.0.0.1:8000/
> - **Admin Dashboard**: http://127.0.0.1:8000/dashboard/
> - **Admin Login**: http://127.0.0.1:8000/login/
> - **Customer Login**: http://127.0.0.1:8000/customer-login/

---

## 🗂️ โครงสร้างโปรเจกต์ (Project Structure)

```
myproject/
├── myproject/              # Django Project Config
│   ├── settings.py         # การตั้งค่าระบบ (DB, Media, etc.)
│   ├── urls.py             # Root URL Config
│   └── wsgi.py
├── app/                    # Django App หลัก
│   ├── views.py            # Business Logic ทั้งหมด (34 functions)
│   ├── urls.py             # URL Patterns ทั้งหมด
│   ├── models.py
│   └── templates/          # HTML Templates (24 ไฟล์)
│       ├── base.html           # Admin Base Layout
│       ├── customer_base.html  # Customer Base Layout
│       ├── portal_login.html   # หน้าเลือก Role
│       ├── dashboard.html      # Admin Dashboard
│       ├── booking.html        # รายการจอง
│       ├── customer_payment.html
│       ├── payment_pending.html
│       ├── verify_slips.html   # ตรวจสลิป
│       ├── ticket.html         # E-Ticket
│       ├── my_bookings.html    # ประวัติการจอง
│       └── ...
├── media/                  # ไฟล์สลิปที่อัปโหลด
│   └── slips/
└── manage.py
```

---

## 🌐 URL Map ทั้งหมด

| URL | ฟังก์ชัน | สิทธิ์ |
|---|---|---|
| `/` | Portal Landing | Public |
| `/login/` | Admin Login | Public |
| `/logout/` | Admin Logout | Admin |
| `/dashboard/` | Admin Dashboard | Admin |
| `/customers/` | รายชื่อลูกค้า | Admin |
| `/add/` | เพิ่มลูกค้า | Admin |
| `/update/` | แก้ไขลูกค้า | Admin |
| `/delete/<id>/` | ลบลูกค้า | Admin |
| `/bookings/` | รายการจองทั้งหมด | Admin |
| `/tours/` | แพ็กเกจทัวร์ | Admin |
| `/hotels/` | โรงแรม | Admin |
| `/employee/` | พนักงาน/ไกด์ | Admin |
| `/payment/` | รายการชำระเงิน | Admin |
| `/admin/slips/` | ตรวจสอบสลิป | Admin |
| `/admin/verify-payment/<id>/` | ยืนยันสลิป | Admin |
| `/admin/reject-payment/<id>/` | ปฏิเสธสลิป | Admin |
| `/customer-login/` | Customer Login | Public |
| `/register/` | สมัครสมาชิก | Public |
| `/customer-logout/` | Customer Logout | Customer |
| `/browse/` | หน้าหลัก Customer | Customer |
| `/browse/tours/` | เลือกทัวร์ | Customer |
| `/browse/hotels/` | ดูโรงแรม | Customer |
| `/browse/payment/` | ชำระเงิน | Customer |
| `/browse/my-bookings/` | ประวัติการจอง | Customer |
| `/browse/ticket/<id>/` | E-Ticket | Customer |
| `/browse/pending/<id>/` | รอยืนยันสลิป | Customer |

---

*ระบบได้รับการพัฒนาด้วย Django 6.0 + SQL Server พร้อมสำหรับการใช้งานจริงของธุรกิจท่องเที่ยว*
