"""BrihaspatiFutsal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from Booking.views.futsalbooking import futsalbooking
from Booking.views.booking import FutsalBooking, check_availability, book_court, booking_confirmation
from Shopping.middlewares.auth import auth_middleware

urlpatterns = [
    path('admin/', admin.site.urls),
                  path('', include('Booking.urls')),
    path('', include('Shopping.urls')),
    path('futsal_booking/', auth_middleware(futsalbooking.as_view()), name='futsal-booking'),
    path('futsalbooking_form/', auth_middleware(FutsalBooking.as_view()), name='futsalbooking-form'),
    path('check-availability/', check_availability, name='check-availability'),
    path('book/', auth_middleware(book_court), name='book-court'),
    path('booking-confirmation/', auth_middleware(booking_confirmation), name='booking-confirmation'),
    path('', include('Infofutsal.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Brihaspati Futsal"
