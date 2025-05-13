from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Budget, Expense
from .forms import BudgetForm
from django.db.models import Sum

def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

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
    total_budget = 500000
    spent = Expense.objects.filter(status='approved').aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_budget = total_budget - spent

    return render(request, 'dashboard/staff.html', {
        'total_budget': total_budget,
        'spent': spent,
        'remaining_budget': remaining_budget
    })

def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = BudgetForm()
    return render(request, 'create_budget.html', {'form': form})

def view_expenses(request):
    expenses = Expense.objects.all()
    return render(request, 'view_expenses.html', {'expenses': expenses})
