from django.shortcuts import render, redirect, HttpResponseRedirect
from Booking.models.booking import Booking
from Booking.forms import AddBooking
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from Shopping.models.customer import Customer
from django.views import View
from datetime import date, datetime
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


class FutsalBooking(View):
    def get(self, request):
        try:
            customer = Customer.objects.get(id=request.session.get('customer'))
            context = {
                'customer': customer,
                'today_date': date.today()
            }
            return render(request, 'booking.html', context)
        except Customer.DoesNotExist:
            return redirect('login')

    def post(self, request):
        try:
            customer = Customer.objects.get(id=request.session.get('customer'))
            fullname = request.POST.get('fullname')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            date = request.POST.get('date')
            time = request.POST.get('time')
            playing_hours = request.POST.get('playing_hours')
            court = request.POST.get('court') 
            
            # Create booking object
            booking = Booking(
                fullname=fullname,
                customer=customer,
                email=email,
                phone=phone,
                address=address,
                date=date,
                time=time,
                playing_hours=playing_hours,
                court=court,
            )
            
            # Validate booking
            error_message = self.validateBooking(booking)
            if error_message:
                return render(request, 'booking.html', {
                    'error': error_message,
                    'customer': customer,
                    'today_date': date.today()
                })
            
            # Save booking
            booking.save()
            
            # Send confirmation email
            template = render_to_string('Userfutsalbooking_email.html', {
                'fullname': fullname,
                'date': date,
                'time': time,
                'playing_hours': playing_hours
            })
            send_mail(
                'Futsal Booked Successfully!',
                template,
                'Brihaspatifutsal2018@gmail.com',
                [email],
                fail_silently=False,
            )
            
            return redirect('send-mail')
            
        except Customer.DoesNotExist:
            return redirect('login')

    def validateBooking(self, booking):
        error_message = None
        if not booking.fullname:
            error_message = "Full Name Required!"
        elif len(booking.fullname) < 4:
            error_message = "Full Name must be 4 char long or more."
        elif not booking.address:
            error_message = "Address Required"
        elif len(booking.address) < 4:
            error_message = "Address must be 4 char long or more."
        elif not booking.phone:
            error_message = "Phone Number Required."
        elif len(booking.phone) < 10 or len(booking.phone) > 10:
            error_message = "Phone Number must be 10 char long."
        elif not booking.handlePlayingHours():
            error_message = "Playing hours should be a positive number."
        elif booking.timeisExists():
            error_message = "Futsal is Booked at this Time."
        return error_message

def add_booking(request):
    if request.method == 'POST':
        fm = AddBooking(request.POST)
        if fm.is_valid():
            fullname = fm.cleaned_data['fullname']
            phone = fm.cleaned_data['phone']
            address = fm.cleaned_data['address']
            date = fm.cleaned_data['date']
            time = fm.cleaned_data['time']
            playing_hours = fm.cleaned_data['playing_hours']
            reg = Booking(fullname=fullname, phone=phone, address=address, date=date, time=time,
                          playing_hours=playing_hours)
            reg.save()
            fm = AddBooking()
            return redirect('bookings')
    else:
        fm = AddBooking()
    return render(request, 'add_booking.html', {'form': fm})


def delete_booking(request, id):
    if request.method == 'POST':
        db = Booking.objects.get(pk=id)
        db.delete()
        return HttpResponseRedirect('/bookings')


def update_booking(request, id):
    if request.method == 'POST':
        pi = Booking.objects.get(pk=id)
        fm = AddBooking(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
            return redirect('bookings')
        else:
            pi = Booking.objects.get(pk=id)
            fm = AddBooking(instance=pi)
    else:
        pi = Booking.objects.get(pk=id)
        fm = AddBooking(instance=pi)
    return render(request, 'update_booking.html', {'form': fm})


def sendfutsalmail(request):
    send_mail(
        'New Futsal Time have been Booked!',
        'Hi , This is a mail to confirm that new Futsal Time have been booked. Please check admin dashboard and confirm the bookings.',
        'Brihaspatifutsal2018@gmail.com',
        ['kritikathapa1011@gmail.com'],
        fail_silently=False,
    )
    return redirect('bookings')

def check_availability(request):
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        try:
            # Get all bookings for the selected date
            bookings = Booking.objects.filter(date=selected_date)
            booked_slots = []
            
            for booking in bookings:
                booked_slots.append({
                    'court': str(booking.court) if hasattr(booking, 'court') else '1',
                    'time': booking.time.strftime('%H:%M') if booking.time else '',
                    'playing_hour': str(booking.playing_hours) if hasattr(booking, 'playing_hours') else '1',
                })
            
            return JsonResponse({
                'success': True,
                'booked_slots': booked_slots
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

def booking_confirmation(request):
    try:
        customer = Customer.objects.get(id=request.session.get('customer'))
        # Get the latest booking for this customer
        latest_booking = Booking.objects.filter(customer=customer).order_by('-booked_at').first()
        
        if latest_booking:
            context = {
                'booking': latest_booking,
                'customer': customer,
            }
            return render(request, 'booking/booking_confirmation.html', context)
        else:
            return redirect('futsal-booking')
    except Customer.DoesNotExist:
        return redirect('login')

@csrf_exempt
def book_court(request):
    if request.method == 'POST':
        try:
            print("POST Data Received:", request.POST)
            customer = Customer.objects.get(id=request.session.get('customer'))
            
            # Get booking details from POST data
            fullname = request.POST.get('fullname', customer.first_name + ' ' + customer.last_name)
            email = request.POST.get('email', customer.email)
            phone = request.POST.get('phone', customer.phone)
            address = request.POST.get('address', '')
            booking_date = request.POST.get('date')
            time_slot = request.POST.get('time')
            playing_hours = request.POST.get('playing_hours', 1)
            court = request.POST.get('court')
            
            # Convert time from 12-hour to 24-hour format
            time_obj = datetime.strptime(time_slot, '%I:%M %p').time()
            
            # Check if the specific court and timeslot is already booked
            if Booking.objects.filter(date=booking_date, time=time_obj, court=court).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'This time slot for the selected court is already booked.'
                })
            
            # Create booking
            booking = Booking(
                fullname=fullname,
                customer=customer,
                email=email,
                phone=phone,
                address=address,
                date=booking_date,
                time=time_obj,
                playing_hours=playing_hours,
                court=court,
            )
            
            # Save booking
            booking.save()
            
            # Send confirmation email
            template = render_to_string('Userfutsalbooking_email.html', {
                'fullname': fullname,
                'date': booking_date,
                'time': time_slot,
                'playing_hours': playing_hours
            })
            send_mail(
                'Futsal Booked Successfully!',
                template,
                'Brihaspatifutsal2018@gmail.com',
                [email],
                fail_silently=False,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Booking successful!'
            })
            
        except Customer.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Please login to make a booking'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })
