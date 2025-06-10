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
    total_budget = Budget.objects.filter(user=request.user).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    spent = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_budget = total_budget - spent
    budgets = Budget.objects.filter(user=request.user).order_by('-start_date')[:4]
    expenses = Expense.objects.filter(user=request.user).order_by('-updated_at')[:4]
    finance_status = "❌Bad" if total_budget < spent else "✅Good"

    return render(request, 'dashboard/normal.html', {
        'total_budget': total_budget,
        'spent': spent,
        'remaining_budget': remaining_budget,
        'budgets': budgets,
        'expenses': expenses,
        'finance_status': finance_status,
    })

def expert_dashboard(request):
    return render(request, 'dashboard/expert.html')

def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')

def staff_dashboard(request):
    total_budget = Budget.objects.filter(user=request.user).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    spent = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_budget = total_budget - spent
    budgets = Budget.objects.filter(user=request.user).order_by('-start_date')[:4]
    expenses = Expense.objects.filter(user=request.user).order_by('-updated_at')[:4]
    finance_status = "❌Bad" if total_budget < spent else "✅Good"
    return render(request, 'dashboard/staff.html', {
        'total_budget': total_budget,
        'spent': spent,
        'remaining_budget': remaining_budget,
        'budgets': budgets,
        'expenses': expenses,
        'finance_status': finance_status,
    })

def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('staff_dashboard')
        else:
            print(form.errors)
            messages.error(request, "Error creating budget.")
            return redirect('staff_dashboard')
    else:
        form = BudgetForm()
    return render(request, 'dashboard/staff.html', {'form': form})

def view_expenses(request):
    expenses = Expense.objects.all()
    return render(request, 'view_expenses.html', {'expenses': expenses})

@login_required
def upload_expense(request):
    budgets = Budget.objects.filter(user=request.user)
    if request.method == 'POST':
        title = request.POST['title']
        amount = request.POST['amount']
        description = request.POST.get('description', '')
        status = request.POST['status']
        budget_id = request.POST['budget_id']

        Expense.objects.create(
            user=request.user,
            budget_id=budget_id,
            name=title,
            amount=amount,
            description=description,
            status=status
        )
        return redirect('staff_dashboard')

    return render(request, 'staff/expenses.html', {'budgets': budgets})
