from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils import timezone
from .models import Profile, UserProfile, StaffProfile, ExpertProfile
from .models import Budget, BudgetCategory, Expense
from .forms import RegisterForm
from decimal import Decimal

def home_view(request):
    return render(request, 'home.html')

def auth_view(request):
    form_login = AuthenticationForm(request, data=request.POST if 'signin' in request.POST else None)
    form_register = RegisterForm(request.POST if 'signup' in request.POST else None)
   
    if request.method == 'POST':
        if 'signup' in request.POST :
            if form_register.is_valid():
                form_register.save()
                messages.success(request, "Registration successful. Please log in.")
                return redirect('/auth/?show_login=true')
            
        elif 'signin' in request.POST :
            if form_login.is_valid():
                user = form_login.get_user()
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid Credentials.")
                return redirect('/auth/?show_login=true')
    
    return render(request, 'auth.html', {
        'form_login': form_login,
        'form_register': form_register
    })

def login_view(request):
    return redirect('/auth/?show_login=true')

def logout_view(request):
    logout(request)
    messages.success(request, "Logout successful.")
    return redirect('/auth/?show_login=true')

@login_required
def dashboard_view(request):
    role = request.user.profile.role
    if role == 'NormalUser':
        return redirect('normal_dashboard')
    elif role == 'CompanyStaff':
        return redirect('staff_dashboard')
    elif role == 'FinanceExpert':
        return redirect('expert_dashboard')
    elif request.user.is_superuser:
        return redirect('admin_dashboard')
    else:
        messages.error(request, "Invalid Role.")
        return redirect('login')
    
def normal_dashboard(request):
    return render(request, 'dashboard/normal.html')

def expert_dashboard(request):
    return render(request, 'dashboard/expert.html')

def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')

def staff_dashboard(request):
    return render(request, 'dashboard/staff.html')

@login_required
def profile(request):
    role = request.user.profile.role
    if role == 'NormalUser':
        return redirect('user_profile')
    elif role == 'CompanyStaff':
        return redirect('staff_profile')
    elif role == 'FinanceExpert':
        return redirect('expert_profile')
    else:
        messages.error(request, "Invalid Role.")
        return redirect('login')

@login_required
def user_profile(request):
    try:
        profile = Profile.objects.get(user=request.user, role='NormalUser')
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            request.user.email = request.POST.get('email')
            user_profile.occupation = request.POST.get('occupation')
            monthly_income = request.POST.get('monthly_income')
            user_profile.monthly_income = Decimal(monthly_income) if monthly_income else None
            user_profile.financial_goals = request.POST.get('financial_goals')
            if 'profile_pic' in request.FILES:
                user_profile.profile_pic = request.FILES['profile_pic']
            request.user.save()
            user_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')
        return render(request, 'profile/user_profile.html', {'user_profile': user_profile})
    except (Profile.DoesNotExist, UserProfile.DoesNotExist):
        raise Http404("Profile not found.")

@login_required
def staff_profile(request):
    try:
        profile = Profile.objects.get(user=request.user, role='CompanyStaff')
        staff_profile, created = StaffProfile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            request.user.email = request.POST.get('email')
            staff_profile.department = request.POST.get('department')
            staff_profile.work_phone = request.POST.get('work_phone')
            if 'profile_pic' in request.FILES:
                staff_profile.profile_pic = request.FILES['profile_pic']
            request.user.save()
            staff_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('staff_profile')
        return render(request, 'profile/staff_profile.html', {'staff_profile': staff_profile})
    except (Profile.DoesNotExist, StaffProfile.DoesNotExist):
        raise Http404("Profile not found.")

@login_required
def expert_profile(request):
    try:
        profile = Profile.objects.get(user=request.user, role='FinanceExpert')
        expert_profile, created = ExpertProfile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            request.user.email = request.POST.get('email')
            expert_profile.expertise_area = request.POST.get('expertise_area')
            consultation_fee = request.POST.get('consultation_fee')
            expert_profile.consultation_fee = Decimal(consultation_fee) if consultation_fee else None
            expert_profile.available_times = request.POST.get('available_times')
            expert_profile.bio = request.POST.get('bio')
            if 'profile_pic' in request.FILES:
                expert_profile.profile_pic = request.FILES['profile_pic']
            if 'certificates' in request.FILES:
                expert_profile.certificates = request.FILES['certificates']
            request.user.save()
            expert_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('expert_profile')
        return render(request, 'profile/expert_profile.html', {'expert_profile': expert_profile})
    except (Profile.DoesNotExist, ExpertProfile.DoesNotExist):
        raise Http404("Profile not found.")

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'budget/budget_list.html', {'budgets': budgets})

@login_required
def create_budget(request):
    if request.method == 'POST':
        month = request.POST.get('month')
        total_income = request.POST.get('total_income')
        categories = request.POST.getlist('categories')
        limits = request.POST.getlist('limits')

        if Budget.objects.filter(user=request.user, month=month).exists():
            messages.error(request, 'Budget for this month already exists.')
            return redirect('create_budget')

        try:
            budget = Budget.objects.create(
                user=request.user,
                month=month,
                total_income=Decimal(total_income),
                total_budgeted=Decimal(sum(float(limit) for limit in limits))
            )
            for name, limit in zip(categories, limits):
                if name and limit:
                    BudgetCategory.objects.create(
                        budget=budget,
                        name=name,
                        limit=Decimal(limit)
                    )
            messages.success(request, 'Budget created successfully!')
            return redirect('budget_list')
        except ValueError:
            messages.error(request, 'Invalid input. Please check your data.')
            return redirect('create_budget')

    return render(request, 'budget/create_budget.html', {})

@login_required
def budget_detail(request, budget_id):
    try:
        budget = Budget.objects.get(id=budget_id, user=request.user)
        for category in budget.categories.all():
            category.spent = sum(expense.amount for expense in category.expenses.all())
            category.remaining = category.limit - category.spent
        return render(request, 'budget/budget_detail.html', {'budget': budget})
    except Budget.DoesNotExist:
        raise Http404("Budget not found.")
    
@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'budget/expense_list.html', {'expenses': expenses})

@login_required
def add_expense(request):
    categories = BudgetCategory.objects.filter(budget__user=request.user)
    if request.method == 'POST':
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        date = request.POST.get('date')

        try:
            category = BudgetCategory.objects.get(id=category_id, budget__user=request.user)
            expense = Expense.objects.create(
                user=request.user,
                category=category,
                amount=Decimal(amount),
                note=note,
                date=date or timezone.now().date()
            )
            # Update budget's total_spent
            budget = category.budget
            budget.total_spent += expense.amount
            budget.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_list')
        except (BudgetCategory.DoesNotExist, ValueError):
            messages.error(request, 'Invalid input. Please check your data.')
            return redirect('add_expense')

    return render(request, 'budget/add_expense.html', {'categories': categories})