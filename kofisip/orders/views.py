from django.shortcuts import render, redirect
from .models import MenuItem, Order, OrderItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone

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