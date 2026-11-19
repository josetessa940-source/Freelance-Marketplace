from django.urls import path
from .import views
urlpatterns = [
    path('',views.home,name='home'),
    path('register/',views.register,name='register'),
    path('logn/',views.logn,name='logn'),
    path('logot/',views.logot,name='logot'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('reset_password/<uidb64>/<str:token>/',views.reset_password,name='reset_password'),
    path('verify_email/<uidb64>/<str:token>/', views.verify_email,name='verify_email'),
    path('profile/',views.profile,name='profile'),
    path('freelancer_profile/',views.freelancer_profile,name='freelancer_profile'),
    path('portfolio/',views.portfolio,name='portfolio'),
    path('view_portfolio/', views.view_portfolio, name='view_portfolio'),
    path('edit_portfolio/<int:id>/', views.edit_portfolio, name='edit_portfolio'),
    path('delete_portfolio/<int:id>/', views.delete_portfolio, name='delete_portfolio'),
]