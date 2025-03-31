from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import datetime
from ..models import Court, CourtBooking
import logging
import json

logger = logging.getLogger(__name__)

def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

@login_required
@ensure_csrf_cookie
def booking_page(request):
    courts = Court.objects.all()
    context = {
        'courts': courts,
        'today_date': datetime.now().date()
    }
    return render(request, 'booking/booking.html', context)

@login_required
@require_http_methods(["GET"])
def check_availability(request):
    try:
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({
                'success': False,
                'error': 'Date parameter is required'
            })
            
        logger.info(f"Checking availability for date: {date_str}")
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get all bookings for the selected date
        booked_slots = CourtBooking.objects.filter(
            booking_date=booking_date
        ).values(
            'court__id',
            'court__name',
            'start_time',
            'duration'
        )
        
        # Format the booked slots for the frontend
        formatted_slots = []
        for slot in booked_slots:
            formatted_slots.append({
                'court_id': slot['court__id'],
                'court_name': slot['court__name'],
                'start_time': slot['start_time'].strftime('%H:%M'),
                'duration': slot['duration']
            })
        
        # Get all courts for availability check
        all_courts = list(Court.objects.values('id', 'name', 'court_type', 'price_per_hour'))
        
        return JsonResponse({
            'success': True,
            'booked_slots': formatted_slots,
            'courts': all_courts
        })
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid date format'
        })
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["POST"])
def book_court(request):
    try:
        # Get booking details from POST data
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        court_id = request.POST.get('court_id')
        duration = int(request.POST.get('playing_hours', 1))
        
        if not all([date_str, time_str, court_id, duration]):
            return JsonResponse({
                'success': False,
                'error': 'All fields are required'
            })
        
        # Convert strings to proper datetime objects
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(time_str, '%H:%M').time()
        
        # Get the court
        try:
            court = Court.objects.get(id=court_id)
        except Court.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invalid court selected'
            })
        
        # Check if the slot is already booked
        if CourtBooking.objects.filter(
            court=court,
            booking_date=booking_date,
            start_time=start_time
        ).exists():
            return JsonResponse({
                'success': False,
                'error': 'This slot is already booked.'
            })
        
        # Calculate total price
        total_price = court.price_per_hour * duration
        
        # Create the booking
        booking = CourtBooking.objects.create(
            user=request.user,
            court=court,
            booking_date=booking_date,
            start_time=start_time,
            duration=duration,
            total_price=total_price
        )
        
        if is_ajax(request):
            return JsonResponse({
                'success': True,
                'booking_id': booking.id,
                'redirect_url': f'/booking/booking-confirmation/{booking.id}/'
            })
        else:
            return redirect('booking:booking_confirmation_with_id', booking_id=booking.id)
        
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        if is_ajax(request):
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        else:
            return redirect('booking:booking_page')

@login_required
def booking_confirmation(request, booking_id=None):
    try:
        if booking_id:
            booking = CourtBooking.objects.get(id=booking_id, user=request.user)
        else:
            booking = CourtBooking.objects.filter(user=request.user).latest('created_at')
        
        context = {
            'booking': booking,
            'user': request.user
        }
        return render(request, 'booking/booking_confirmation.html', context)
    except CourtBooking.DoesNotExist:
        return redirect('booking:booking_page') 