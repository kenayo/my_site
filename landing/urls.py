from django.conf.urls import url, include
from django.contrib import admin
from . import views
from landing import views


urlpatterns = [
    url(r'^landing/', views.landing, name='landing')
]