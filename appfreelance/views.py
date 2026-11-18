from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
from .forms import *
from .serializers import *
from django.contrib import messages
from django .contrib.auth import authenticate,login,logout
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
# Create your views here.

def home(request):
    return render(request,'home.html')

def register(request):
    if request.method=="POST":
        form=RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration completed successfully!")
            return redirect('register')
    else:
        form=RegistrationForm()
    return render(request,'register.html',{'form':form})

def logn(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not  None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"Invalid username or password.")
    return render(request,'login.html')

def logot(request):
    logout(request)
    return redirect('home')

def forgot_password(request):
    if request.method=='POST':
        email=request.POST.get('email')
        user_model=get_user_model()
        user=user_model.objects.filter(email=email).first()
        if user:
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            token=default_token_generator.make_token(user)
            reset_url=request.build_absolute_uri(reverse('reset_password',
                                                         kwargs={'uidb64':uid,'token':token}))
            subject='Password Reset Request'
            message=f"""Hello {user.username},
            You requested a password reset.
            Click the link below to reset your password:{reset_url}
            if you did not request this,ignore this email."""
            send_mail(subject,message,settings.DEFAULT_FROM_EMAIL,[user.email],fail_silently=False)
            messages.success(request,"Password reset link has been sent")
            return redirect('forgot_password')
        else:
            messages.error(request,"Invalid email address")
    return render(request,'forgot_password.html')

def reset_password(request,uidb64,token):
    user_model=get_user_model()
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user=user_model.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        if request.method == 'POST':
            password=request.POST.get('password')
            confirm_password=request.POST.get('confirm_password')
            if password !=confirm_password:
                messages.error(request,"Passwords do not match")
            else:
                try:
                    validate_password(password,user)
                    user.set_password(password)
                    user.save()
                    messages.success(request,"Password changed successfully!")
                    return redirect('logn')
                except ValidationError as e:
                    for error in e.messages:
                        messages.error(request,error)
        return render(request,'reset_password.html')
    return render(request,'invalid_reset_link.html')