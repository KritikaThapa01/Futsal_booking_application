from django.views import View
from django.shortcuts import render, redirect
from Shopping.models.customer import Customer
from django.contrib import messages
from Booking.models import Court, CourtBooking
from datetime import datetime, date
from django.utils.decorators import method_decorator
from Shopping.middlewares.auth import auth_required

@method_decorator(auth_required, name='dispatch')
class futsalbooking(View):
    def get(self, request):
        try:
            customer = Customer.objects.get(id=request.session.get('customer'))
            context = {
                'customer': customer,
                'customers': [customer],
                'today': date.today()
            }
            return render(request, 'futsalbooking.html', context)
        except Customer.DoesNotExist:
            return redirect('login')

    def post(self, request):
        try:
            customer = Customer.objects.get(id=request.session.get('customer'))
        except Customer.DoesNotExist:
            return redirect('login')
        
        return redirect('booking:futsalbooking-form')