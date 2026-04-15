from django.urls import path
from . import views

urlpatterns = [
    # ── PORTAL LANDING (หน้าเลือก Admin / Customer) ──────────
    path('',               views.portal_landing,         name='portal'),

    # ── ADMIN AUTH ────────────────────────────────────────────
    path('login/',         views.login_view,             name='admin-login'),
    path('logout/',        views.logout_view,            name='admin-logout'),

    # ── ADMIN DASHBOARD & MANAGEMENT ─────────────────────────
    path('dashboard/',     views.dashboard,              name='dashboard'),
    path('customers/',     views.customer_list,          name='customers'),
    path('add/',           views.add_customer,           name='add-customer'),
    path('update/',        views.update_customer,        name='update-customer'),
    path('delete/<int:id>/',views.delete_customer,       name='delete-customer'),
    path('bookings/',      views.booking_list,           name='bookings'),
    path('tours/',         views.tour_list,              name='tours'),
    path('hotels/',        views.hotel_list,             name='hotels'),
    path('employee/',      views.employee_list,          name='employees'),
    path('payment/',       views.payment_page,           name='payment'),
    path('confirm-payment/', views.confirm_payment,      name='confirm-payment'),

    # ── CUSTOMER AUTH ─────────────────────────────────────────
    path('customer-login/', views.customer_login_view,  name='customer-login'),
    path('register/',       views.register_view,        name='register'),
    path('customer-logout/',views.customer_logout_view, name='customer-logout'),

    # ── CUSTOMER PORTAL ───────────────────────────────────────
    path('browse/',              views.customer_home,           name='customer-home'),
    path('browse/tours/',        views.customer_tours,          name='customer-tours'),
    path('browse/hotels/',       views.customer_hotels,         name='customer-hotels'),
    path('browse/my-bookings/',  views.my_bookings,             name='my-bookings'),
    path('browse/payment/',      views.customer_payment_page,   name='customer-payment'),
    path('browse/confirm-payment/', views.customer_confirm_payment, name='customer-confirm-payment'),
    path('browse/book-hotel/',   views.book_hotel,              name='book-hotel'),
    path('browse/ticket/<int:booking_id>/', views.ticket_view, name='ticket'),
    path('browse/pending/<int:booking_id>/', views.payment_pending_view, name='payment-pending'),

    # ── ADMIN SLIP VERIFY ────────────────────────────────────
    path('admin/slips/',                          views.admin_slip_list,      name='admin-slips'),
    path('admin/verify-payment/<int:payment_id>/', views.admin_verify_payment, name='verify-payment'),
    path('admin/reject-payment/<int:payment_id>/', views.admin_reject_payment, name='reject-payment'),
    
]