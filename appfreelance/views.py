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
from django.core.paginator import Paginator
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
    client_form = None
    freelancer = None
    client = None

    if request.user.is_freelancer:
        freelancer, created = FreelancerProfile.objects.get_or_create(
            user=request.user)
        freelancer_form = FreelancerProfileForm(instance=freelancer)

    if request.user.is_client:
        client, created = ClientProfile.objects.get_or_create(
            user=request.user)
        client_form = ClientProfileForm(instance=client)

    if request.method == "POST":
        user_form = UserProfileForm(
            request.POST, instance=request.user)

        if request.user.is_freelancer:
            freelancer_form = FreelancerProfileForm(
                request.POST, instance=freelancer)

        if request.user.is_client:
            client_form = ClientProfileForm(
                request.POST, instance=client)

        if user_form.is_valid():
            if freelancer_form is None or freelancer_form.is_valid():
                if client_form is None or client_form.is_valid():

                    user_form.save()

                    if freelancer_form:
                        freelancer_form.save()

                    if client_form:
                        client_form.save()

                    messages.success(
                        request, "Profile updated successfully!")
                    return redirect('profile')

    return render(request, 'profile.html', {
        'user_form': user_form,'freelancer_form': freelancer_form,'client_form': client_form})

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

def create_project(request):
    if not request.user.is_authenticated:
        return redirect('logn')
    if not request.user.is_client:
        return redirect('profile')
    if request.method=='POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project=form.save(commit=False)
            project.client=request.user
            project.save()
            messages.success(request,"Project created successfully!")
            return redirect('profile')
    else:
        form=ProjectForm()
    return render(request,'project_form.html',{'form':form})

def my_projects(request):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_client:
        return redirect('profile')

    status = request.GET.get('status')

    projects = Project.objects.filter(client=request.user)

    if status:
        projects = projects.filter(status=status)

    return render(request, 'my_projects.html', {'projects': projects})

def edit_project(request, id):
    if not request.user.is_authenticated:
        return redirect('logn')

    project = get_object_or_404(Project, id=id)

    if project.client != request.user and not request.user.is_staff:
        return redirect('profile')

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            return redirect('profile')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'project_form.html', {'form': form})
def publish_project(request, id):
    if not request.user.is_authenticated:
        return redirect('logn')
    if not request.user.is_client:
        return redirect('profile')
    project = get_object_or_404(Project, id=id, client=request.user)
    if request.method == "POST" and project.status == 'draft':
        project.status='published'
        project.save()
        messages.success(request,"Project published successfully!")
    return redirect('my_projects')

def pause_project(request, id):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_client:
        return redirect('profile')

    project = get_object_or_404(Project, id=id, client=request.user)

    if request.method == "POST" and project.status == 'published':
        project.status = 'paused'
        project.save()
        messages.success(request, "Project paused successfully!")

    return redirect('my_projects')

def close_project(request, id):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_client:
        return redirect('profile')

    project = get_object_or_404(Project, id=id, client=request.user)

    if request.method == "POST" and project.status in ['published', 'paused']:
        project.status = 'closed'
        project.save()
        messages.success(request, "Project closed successfully!")

    return redirect('my_projects')

def archive_project(request, id):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_client:
        return redirect('profile')

    project = get_object_or_404(Project, id=id, client=request.user)

    if request.method == "POST" and project.status == 'closed':
        project.status = 'archived'
        project.save()
        messages.success(request, "Project archived successfully!")

    return redirect('my_projects')

def browse_projects(request):
    projects=Project.objects.filter(status='published').order_by('-id')
    return render(request,'browse_projects.html',{'projects':projects})

def browse_projects(request):
    search = request.GET.get('search')

    projects = Project.objects.filter(status='published').order_by('-id')

    if search:
        projects = projects.filter(
            title__icontains=search
        ) | projects.filter(
            description__icontains=search
        ) | projects.filter(
            required_skills__icontains=search
        )

    return render(request, 'browse_projects.html', {'projects': projects })

def browse_projects(request):
    search = request.GET.get('search')
    min_budget = request.GET.get('min_budget')
    max_budget = request.GET.get('max_budget')
    sort_by = request.GET.get('sort_by')

    projects = Project.objects.filter(status='published').order_by('-id')

    if search:
        projects = projects.filter(
            title__icontains=search
        ) | projects.filter(
            description__icontains=search
        ) | projects.filter(
            required_skills__icontains=search
        )

    if min_budget:
        projects = projects.filter(budget__gte=min_budget)

    if max_budget:
        projects = projects.filter(budget__lte=max_budget)

    if sort_by == 'budget_low':
        projects = projects.order_by('budget')

    elif sort_by == 'budget_high':
        projects = projects.order_by('-budget')

    elif sort_by == 'newest':
        projects = projects.order_by('-id')

    elif sort_by == 'oldest':
        projects = projects.order_by('id')
    paginator = Paginator(projects, 5)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)

    return render(request, 'browse_projects.html', {'projects': projects})

def submit_proposal(request, id):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_freelancer:
        return redirect('profile')

    project = get_object_or_404(Project, id=id)
    if Proposal.objects.filter(project=project,freelancer=request.user,status='pending').exists():
        messages.error(request, "You have already submitted a proposal for this project.")
        return redirect('browse_projects')
    if project.status != 'published':
        messages.error(request, "This project is not accepting proposals.")
        return redirect('browse_projects')

    if request.method == "POST":
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.project = project
            proposal.freelancer = request.user
            proposal.save()
            messages.success(request, "Proposal submitted successfully!")
            return redirect('browse_projects')
    else:
        form = ProposalForm()

    return render(request, 'proposal_form.html', {'form': form,'project': project})

def view_proposals(request, id):
    if not request.user.is_authenticated:
        return redirect('logn')

    if not request.user.is_client:
        return redirect('profile')

    project = get_object_or_404(Project, id=id, client=request.user)

    proposals = Proposal.objects.filter(project=project)

    return render(request,
                  'view_proposals.html', {'project': project,'proposals': proposals})

def accept_proposal(request, id):
    if not request.user.is_authenticated or not request.user.is_client:
        return redirect('profile')

    proposal = get_object_or_404(Proposal,id=id,project__client=request.user)

    if request.method == "POST" and proposal.status == 'pending':
        proposal.status = 'accepted'
        proposal.save()
        messages.success(request, "Proposal accepted successfully!")

    return redirect('view_proposals', id=proposal.project.id)

def reject_proposal(request, id):
    if not request.user.is_authenticated or not request.user.is_client:
        return redirect('profile')

    proposal = get_object_or_404(Proposal,id=id,project__client=request.user)

    if request.method == "POST" and proposal.status == 'pending':
        proposal.status = 'rejected'
        proposal.save()
        messages.success(request, "Proposal rejected successfully!")

    return redirect('view_proposals', id=proposal.project.id)