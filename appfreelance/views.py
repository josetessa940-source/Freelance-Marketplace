from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
from .forms import *
from .serializers import *
from django.contrib import messages
from django .contrib.auth import authenticate,login,logout
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