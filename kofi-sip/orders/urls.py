from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('create-order/', views.create_order, name='create_order'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('print-bill/<int:order_id>/', views.print_bill, name='print_bill'),
    path('daily-report/', views.daily_report, name='daily_report'),
    path('monthly-report/', views.monthly_report, name='monthly_report'),
    path('report-issue/', views.report_issue, name='report_issue'),
    path('create-payment/<int:order_id>/', views.create_payment, name='create_payment'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
]