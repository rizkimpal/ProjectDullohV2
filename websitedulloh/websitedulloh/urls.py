from django.contrib import admin
from django.urls import include,path,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    re_path(r'^$',views.index),
    re_path(r'^background/',include('background.urls')),
    re_path(r'^objek/',include('objek.urls')),
    re_path(r'^analisisFFT-final/',include('analisisFFT.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
