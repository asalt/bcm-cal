"""
URL configuration for bcm_cal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.views.generic import RedirectView
from booking import views as booking_views
from django.views.generic import RedirectView 


urlpatterns = [
    path('admin/', admin.site.urls),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('booking/', include('booking.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # For authentication
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', booking_views.signup, name='signup'),  # Add this line
    path('', RedirectView.as_view(url='booking/available_slots/')),  # Redirect root to available_slots
]

