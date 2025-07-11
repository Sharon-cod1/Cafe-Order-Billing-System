from django.shortcuts import render, redirect
from .models import MenuItem, Order, OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from .models import Staff,Shift
import razorpay
from django.conf import settings
from django.contrib import messages

def menu(request):
    categories = {
        'CHICKEN': MenuItem.objects.filter(category='CHICKEN', available=True),
        'SNACKS': MenuItem.objects.filter(category='SNACKS', available=True),
        'DRINKS': MenuItem.objects.filter(category='DRINKS', available=True),
        'DESSERTS': MenuItem.objects.filter(category='DESSERTS', available=True),
        'OTHER': MenuItem.objects.filter(category='OTHER', available=True),
    }
    return render(request, 'orders/menu.html', {'categories': categories})

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_number = data.get('table_number')
        items = data.get('items')
        
        order = Order.objects.create(table_number=table_number)
        total_amount = 0
        
        for item in items:
            menu_item = MenuItem.objects.get(id=item['id'])
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item['quantity'],
                price=menu_item.price
            )
            total_amount += menu_item.price * item['quantity']
        
        order.total_amount = total_amount
        order.save()
        
        return JsonResponse({'order_id': order.id})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})

def print_bill(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/bill.html', {'order': order})

def daily_report(request):
    today = timezone.now().date()
    orders = Order.objects.filter(order_time__date=today)
    total_sales = sum(order.total_amount for order in orders)
    return render(request, 'orders/daily_report.html', {
        'orders': orders,
        'total_sales': total_sales,
        'date': today
    })

def monthly_report(request):
    month = timezone.now().month
    year = timezone.now().year
    orders = Order.objects.filter(order_time__month=month, order_time__year=year)
    total_sales = sum(order.total_amount for order in orders)
    return render(request, 'orders/monthly_report.html', {
        'orders': orders,
        'total_sales': total_sales,
        'month': month,
        'year': year
    })

def staff_login(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')
        try:
            staff = Staff.objects.get(pin_code=pin, is_active=True)
            # End any active shifts
            Shift.objects.filter(staff=staff, is_active=True).update(
                end_time=timezone.now(), 
                is_active=False
            )
            # Start new shift
            Shift.objects.create(staff=staff)
            request.session['staff_id'] = staff.id
            return redirect('menu')
        except Staff.DoesNotExist:
            return render(request, 'orders/staff_login.html', {'error': 'Invalid PIN'})
    return render(request, 'orders/staff_login.html')

def staff_logout(request):
    staff_id = request.session.get('staff_id')
    if staff_id:
        Shift.objects.filter(staff_id=staff_id, is_active=True).update(
            end_time=timezone.now(),
            is_active=False
        )
        del request.session['staff_id']
    return redirect('staff_login')

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_payment(request, order_id):
    order = Order.objects.get(id=order_id)
    amount = int(order.total_amount * 100)  # Razorpay uses paise
    payment = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'receipt': f'order_{order_id}'
    })
    return JsonResponse({'id': payment['id']})

def verify_payment(request):
    if request.method == 'POST':
        data = request.POST
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': data.get('razorpay_order_id'),
                'razorpay_payment_id': data.get('razorpay_payment_id'),
                'razorpay_signature': data.get('razorpay_signature')
            })
            order = Order.objects.get(id=data.get('order_id'))
            order.payment_status = 'paid'
            order.payment_id = data.get('razorpay_payment_id')
            order.save()
            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'failed'}, status=400)
        
def report_issue(request):
    if request.method == 'POST':
        issue = request.POST.get('issue')
        if issue:
            # You could save this to a model or email it
            print(f"Reported Issue: {issue}")  # or save to DB/logs
            messages.success(request, 'Problem reported successfully.')
            return redirect('menu')
        else:
            messages.error(request, 'Please describe the issue.')
    return render(request, 'orders/report_problem.html')