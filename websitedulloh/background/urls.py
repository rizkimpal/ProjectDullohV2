from django.urls import path,re_path

from . import views

urlpatterns = [
    re_path(r'^$',views.index),
    path('objek/',views.objek),
    path('analisisFFT/',views.analisisFFT),
]