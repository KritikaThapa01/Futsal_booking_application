from django.contrib import admin
from django.urls import path
from .views.Tregistration import Tregistration
from .views.booking import Booking, FutsalBooking, add_booking, delete_booking, update_booking, sendfutsalmail
from .views.futsalbooking import futsalbooking
from Shopping.middlewares.auth import auth_middleware
from .views.all_bookings import all_booking
from .views.report import showreport
from .views.court_booking import booking_page, check_availability, book_court, booking_confirmation

app_name = 'booking'

urlpatterns = [
    path('futsal_booking', auth_middleware(futsalbooking.as_view()), name='futsal-booking'),
    path('futsalbooking_form', auth_middleware(FutsalBooking.as_view()), name='futsalbooking-form'),
path('Tregistration/', Tregistration.as_view(), name='Tregistration'),
    path('bookings', auth_middleware(all_booking.as_view()), name='bookings'),
    path('update_booking/<int:id>', update_booking, name='update-booking'),
    path('add_booking', auth_middleware(add_booking), name='add-booking'),
    path('delete_booking/<int:id>', delete_booking, name='delete-booking'),
    path('sendmail', sendfutsalmail, name='send-mail'),
    path('report', auth_middleware(showreport), name='report')
]
