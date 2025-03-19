from django.contrib import admin
from django.urls import path
from dash import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signin/', views.signin, name='signin'), 
    path('passwordreset/', views.passwordreset, name='passwordreset'), 
    path('logout/', views.user_logout, name='logout'),
    path("profil/", views.profil, name="profil"),
    path('', views.home, name='home'),  
    path('vm_gsm/', views.vm_gsm, name='vm_gsm'),
    path('superviseurs_gsm/', views.superviseurs_gsm, name='superviseurs_gsm'),
    path('coachs_mobiles_gsm/', views.coachs_mobiles_gsm, name='coachs_mobiles_gsm'),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
