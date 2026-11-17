from django.urls import path
from .import views
urlpatterns = [
    path('',views.home,name='home'),
    path('register',views.register,name='register'),
    path('logn',views.logn,name='logn'),
    path('logot',views.logot,name='logot'),
]