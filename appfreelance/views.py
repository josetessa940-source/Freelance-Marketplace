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
            user=form.save()
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            token=default_token_generator.make_token(user)
            verify_url=request.build_absolute_uri(reverse('verify_email',kwargs=
            {'uidb64':uid,'token':token}))
            subject="Verify Your Email"
            message=f"""Hello{user.username},Thank you for registering.
                            Please click the link below to verify your email:{verify_url} 
                            Thank You."""
            send_mail(subject,message,settings.DEFAULT_FROM_EMAIL,[user.email],fail_silently=False)
            messages.success(request,
                             "Registration successful! Please check your email to verify your account.")
            return redirect('logn')
    else:
            form=RegistrationForm()
    return render(request,'register.html',{'form':form})

def logn(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_email_verified:
                login(request, user)
                return redirect('profile')
            else:
                messages.error(request, "Please verify your email before logging in.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

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

def verify_email(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        user=CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user=None
    if user is None:
        return HttpResponse("Invalid verification link.")
    if user.is_email_verified:
        return HttpResponse("Email already verified.")
    if default_token_generator.check_token(user,token):
        user.is_email_verified=True
        user.save()
        return HttpResponse("Email verified Successfully.")
    return HttpResponse("Invalid or expired verification link.")

def profile(request):
    if not request.user.is_authenticated:
        return redirect('logn')

    user_form = UserProfileForm(instance=request.user)
    freelancer_form = None

    if request.user.is_freelancer:
        freelancer, created = FreelancerProfile.objects.get_or_create(
            user=request.user
        )
        freelancer_form = FreelancerProfileForm(instance=freelancer)

    if request.method == "POST":
        user_form = UserProfileForm(
            request.POST, instance=request.user
        )

        if request.user.is_freelancer:
            freelancer_form = FreelancerProfileForm(
                request.POST, instance=freelancer
            )

        if user_form.is_valid():
            if freelancer_form is None or freelancer_form.is_valid():
                user_form.save()

                if freelancer_form:
                    freelancer_form.save()

                messages.success(request, "Profile updated successfully!")
                return redirect('profile')

    return render(request, 'profile.html', {
        'user_form': user_form,'freelancer_form': freelancer_form})

def freelancer_profile(request):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_freelancer:
        return redirect('profile')

    freelancer, created = FreelancerProfile.objects.get_or_create(
        user=request.user)

    if request.method == "POST":
        form = FreelancerProfileForm(request.POST, instance=freelancer)
        if form.is_valid():
            form.save()
            messages.success(request, "Freelancer profile updated successfully!")
            return redirect('freelancer_profile')
    else:
        form = FreelancerProfileForm(instance=freelancer)

    return render(request, 'freelancer_profile.html', {'form': form})

def portfolio(request):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_freelancer:
        return redirect('profile')

    freelancer = get_object_or_404(
        FreelancerProfile, user=request.user
    )

    if request.method == "POST":
        form = PortfolioItemForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.freelancer = freelancer
            portfolio.save()
            messages.success(request, "Portfolio added successfully!")
            return redirect('profile')
    else:
        form = PortfolioItemForm()

    return render(request, 'portfolio.html', {'form': form})

def view_portfolio(request):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_freelancer:
        return redirect('profile')

    freelancer = get_object_or_404(
        FreelancerProfile, user=request.user
    )

    portfolios = PortfolioItem.objects.filter(freelancer=freelancer)

    return render(request, 'view_portfolio.html', {
        'portfolios': portfolios
    })

def edit_portfolio(request, id):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_freelancer:
        return redirect('profile')

    portfolio = get_object_or_404(
        PortfolioItem,
        id=id,
        freelancer__user=request.user
    )

    if request.method == "POST":
        form = PortfolioItemForm(request.POST, instance=portfolio)

        if form.is_valid():
            form.save()
            messages.success(request, "Portfolio updated successfully!")
            return redirect('view_portfolio')
    else:
        form = PortfolioItemForm(instance=portfolio)

    return render(request, 'edit_portfolio.html', {'form': form})

def delete_portfolio(request, id):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_freelancer:
        return redirect('profile')

    portfolio = get_object_or_404(
        PortfolioItem,
        id=id,
        freelancer__user=request.user
    )

    if request.method == "POST":
        portfolio.delete()
        messages.success(request, "Portfolio deleted successfully!")
        return redirect('view_portfolio')

    return render(request, 'delete_portfolio.html', {
        'portfolio': portfolio
    })