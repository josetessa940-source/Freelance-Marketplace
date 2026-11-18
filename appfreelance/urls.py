from django.urls import path
from .import views
urlpatterns = [
    path('',views.home,name='home'),
    path('register/',views.register,name='register'),
    path('logn/',views.logn,name='logn'),
    path('logot/',views.logot,name='logot'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('reset_password/<uidb64>/<str:token>/',views.reset_password,name='reset_password'),
]