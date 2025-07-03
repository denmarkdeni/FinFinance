from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, F, Q, Avg
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import User
from .models import Profile, UserProfile, StaffProfile, ExpertProfile, CompanyTransaction
from .models import Budget, BudgetCategory, Expense, Booking, Feedback, Notification 
from .forms import RegisterForm
from decimal import Decimal
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from io import BytesIO
import io, json, math, csv

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

@login_required
def expert_dashboard(request):
    if request.user.profile.role != 'FinanceExpert':
        messages.error(request, 'Only finance experts can access this dashboard.')
        return redirect('dashboard')
    
    # Total Appointments
    total_appointments = Booking.objects.filter(expert=request.user).count()

    # Recent Appointments
    recent_appointments = Booking.objects.filter(expert=request.user).select_related('user').order_by('-date_time')[:3]

    # Top Appointments by Feedback Rating
    top_appointments = Booking.objects.filter(expert=request.user).annotate(
        avg_rating=Avg('feedback__rating')
    ).order_by('-avg_rating')[:4]

    # Appointments by Month (Bar Chart)
    appointment_data = Booking.objects.filter(expert=request.user).values('date_time__month', 'date_time__year').annotate(
        total=Count('id')
    ).order_by('date_time__year', 'date_time__month')
    appointment_chart_data = {
        'labels': [f"{b['date_time__month']}/{b['date_time__year']}" for b in appointment_data],
        'data': [b['total'] for b in appointment_data]
    }

    # Appointment Status (Donut Chart)
    status_data = {
        'labels': ['Completed', 'Pending', 'Confirmed', 'Cancelled'],
        'data': [
            Booking.objects.filter(expert=request.user, status='Completed').count(),
            Booking.objects.filter(expert=request.user, status='Pending').count(),
            Booking.objects.filter(expert=request.user, status='Confirmed').count(),
            Booking.objects.filter(expert=request.user, status='Cancelled').count()
        ]
    }

    # Appointment Trend (Area Chart, last 6 months)
    six_months_ago = timezone.now().date() - timedelta(days=180)
    appointment_trend = Booking.objects.filter(expert=request.user, date_time__gte=six_months_ago).values('date_time__month', 'date_time__year').annotate(
        total=Count('id')
    ).order_by('date_time__year', 'date_time__month')
    appointment_trend_data = {
        'labels': [f"{b['date_time__month']}/{b['date_time__year']}" for b in appointment_trend],
        'data': [b['total'] for b in appointment_trend]
    }

    context = {
        'total_appointments': total_appointments,
        'recent_appointments': recent_appointments,
        'top_appointments': top_appointments,
        'appointment_chart_data': json.dumps(appointment_chart_data),
        'status_data': json.dumps(status_data),
        'appointment_trend_data': json.dumps(appointment_trend_data)
    }
    return render(request, 'dashboard/expert.html', context)

@login_required
def staff_dashboard(request):
    if request.user.profile.role != 'CompanyStaff':
        messages.error(request, 'Only company staff can access this dashboard.')
        return redirect('dashboard')
    
    # Total Net Amount
    total_income = CompanyTransaction.objects.filter(type='Incoming').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = CompanyTransaction.objects.filter(type='Outgoing').aggregate(total=Sum('amount'))['total'] or 0
    total_net = total_income - total_expenses

    # Recent Transactions
    recent_transactions = CompanyTransaction.objects.select_related('created_by').order_by('-date')[:3]

    # Top Net Amount Months
    top_months = CompanyTransaction.objects.values('month').annotate(
        total_income=Sum('amount', filter=Q(type='Incoming')),
        total_expenses=Sum('amount', filter=Q(type='Outgoing'))
    ).annotate(
        net_amount=F('total_income') - F('total_expenses')
    ).order_by('-net_amount')[:4]

    # Company Budget by Month (Bar Chart)
    budget_data = CompanyTransaction.objects.values('month').annotate(
        total=Sum('amount', filter=Q(type='Incoming'))
    ).order_by('month')
    budget_chart_data = {
        'labels': [b['month'] for b in budget_data],
        'data': [float(b['total'] or 0) for b in budget_data]
    }

    # Transaction Data (Incoming vs Outgoing, Donut Chart)
    transaction_data = {
        'labels': ['Incoming', 'Outgoing'],
        'data': [float(total_income), float(total_expenses)]
    }

    # Net Amount Trend (Area Chart, last 6 months)
    six_months_ago = timezone.now().date() - timedelta(days=180)
    net_trend = CompanyTransaction.objects.filter(date__gte=six_months_ago).values('month').annotate(
        total_income=Sum('amount', filter=Q(type='Incoming')),
        total_expenses=Sum('amount', filter=Q(type='Outgoing'))
    ).annotate(
        net_amount=F('total_income') - F('total_expenses')
    ).order_by('month')
    net_trend_data = {
        'labels': [b['month'] for b in net_trend],
        'data': [float(b['net_amount'] or 0) for b in net_trend]
    }

    context = {
        'total_net': total_net,
        'recent_transactions': recent_transactions,
        'top_months': top_months,
        'budget_chart_data': json.dumps(budget_chart_data),
        'transaction_data': json.dumps(transaction_data),
        'net_trend_data': json.dumps(net_trend_data)
    }
    return render(request, 'dashboard/staff.html', context)
    
@login_required
def normal_user_dashboard(request):
    if request.user.profile.role != 'NormalUser':
        messages.error(request, 'Only normal users can access this dashboard.')
        return redirect('budget_list')
    
    # Total Budgets and Savings
    total_budgeted = Budget.objects.filter(user=request.user).aggregate(total=Sum('total_budgeted'))['total'] or 0
    total_expenses = Expense.objects.filter(category__budget__user=request.user).aggregate(total=Sum('amount'))['total'] or 0
    total_savings = total_budgeted - total_expenses

    # Recent Bookings
    recent_bookings = Booking.objects.filter(user=request.user).select_related('expert').order_by('-date_time')[:4]

    # Top Budget Months (by savings)
    top_months = Budget.objects.filter(user=request.user).annotate(
        total_expenses=Sum('categories__expenses__amount')
    ).annotate(
        savings=Sum('total_budgeted') - Sum('categories__expenses__amount')
    ).order_by('-savings')[:4]

    # Budget Graph Data (Total Budgeted vs Month)
    budget_data = Budget.objects.filter(user=request.user).values('month').annotate(
        total=Sum('total_budgeted')
    ).order_by('month')
    budget_chart_data = {
        'labels': [b['month'] for b in budget_data],
        'data': [float(b['total'] or 0) for b in budget_data]
    }

    # Category Data (Total Categories Donut Chart)
    category_data = {
        'labels': [c['name'] for c in BudgetCategory.objects.filter(budget__user=request.user).values('name').distinct()[:4]],
        'data': [BudgetCategory.objects.filter(budget__user=request.user, name=c['name']).count() for c in BudgetCategory.objects.filter(budget__user=request.user).values('name').distinct()[:4]]
    }

    # Budget Trend Data (Total Budgeted Area Chart, last 6 months)
    six_months_ago = timezone.now().date() - timedelta(days=180)
    budget_trend = Budget.objects.filter(user=request.user, month__gte=six_months_ago).values('month').annotate(
        total=Sum('total_budgeted')
    ).order_by('month')
    budget_trend_data = {
        'labels': [b['month'] for b in budget_trend],
        'data': [float(b['total'] or 0) for b in budget_trend]
    }

    context = {
        'total_budgeted': total_budgeted,
        'total_savings': total_savings,
        'recent_bookings': recent_bookings,
        'top_months': top_months,
        'budget_chart_data': json.dumps(budget_chart_data),
        'category_data': json.dumps(category_data),
        'budget_trend_data': json.dumps(budget_trend_data)
    }
    return render(request, 'dashboard/normal_user.html', context)

@login_required
def admin_dashboard(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, 'Only company staff can access the admin dashboard.')
        return redirect('budget_list')
    
    # Total Users and Growth
    total_users = User.objects.count()
    user_growth = 5  # Placeholder: Calculate actual growth if data available

    # Total Budgets and Growth
    total_budgets = Budget.objects.aggregate(total=Sum('total_budgeted'))['total'] or 0
    budget_growth = 3  # Placeholder: Calculate actual growth if data available

    # Recent Bookings
    recent_bookings = Booking.objects.select_related('user', 'expert').order_by('-date_time')[:4]

    # Top Budget Managers
    top_managers = User.objects.filter(profile__role='NormalUser').annotate(
        total_budgeted=Sum('budget__total_budgeted'),
        budget_count=Count('budget')
    ).order_by('-total_budgeted')[:3]

    # Budget Graph Data (Users & Budget)
    budget_data = Budget.objects.values('month').annotate(
        total=Sum('total_budgeted')
    ).order_by('month')
    budget_chart_data = {
        'labels': [b['month'] for b in budget_data],
        'data': [float(b['total'] or 0) for b in budget_data]
    }

    # User Role Data (Total Users Donut Chart)
    user_role_data = {
        'labels': ['Normal Users', 'Experts', 'Staffs'],
        'data': [
            Profile.objects.filter(role='NormalUser').count(),
            Profile.objects.filter(role='FinanceExpert').count(),
            Profile.objects.filter(role='CompanyStaff').count()
        ]
    }

    # Budget Trend Data (Total Budgets Area Chart, last 6 months)
    six_months_ago = timezone.now().date() - timedelta(days=180)
    budget_trend = Budget.objects.filter(month__gte=six_months_ago).values('month').annotate(
        total=Sum('total_budgeted')
    ).order_by('month')
    budget_trend_data = {
        'labels': [b['month'] for b in budget_trend],
        'data': [float(b['total'] or 0) for b in budget_trend]
    }

    context = {
        'total_users': total_users,
        'user_growth': user_growth,
        'total_budgets': total_budgets,
        'budget_growth': budget_growth,
        'recent_bookings': recent_bookings,
        'top_managers': top_managers,
        'budget_chart_data': json.dumps(budget_chart_data),
        'user_role_data': json.dumps(user_role_data),
        'budget_trend_data': json.dumps(budget_trend_data)
    }
    return render(request, 'dashboard/admin.html', context)

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
        categories_with_data = []
        for category in budget.categories.all():
            spent = sum(expense.amount for expense in category.expenses.all())
            remaining = category.limit - spent
            categories_with_data.append({
                'name': category.name,
                'limit': category.limit,
                'spent': spent,
                'remaining': remaining,
            })
        return render(request, 'budget/budget_detail.html', {'budget': budget,'categories': categories_with_data,})
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

@login_required
def export_budget_pdf(request, budget_id):
    try:
        budget = Budget.objects.get(id=budget_id, user=request.user)
        categories_data = []
        for category in budget.categories.all():
            spent = sum(expense.amount for expense in category.expenses.all())
            remaining = category.limit - spent
            categories_data.append({
                'name': category.name,
                'limit': category.limit,
                'spent': spent,
                'remaining': remaining,
            })

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        normal_style = styles['Normal']
        status_style = ParagraphStyle(
            name='Status',
            parent=normal_style,
            textColor=colors.black,
            fontSize=10,
            leading=12
        )

        # Title
        elements.append(Paragraph(f"Budget Summary for {budget.month}", title_style))
        elements.append(Spacer(1, 0.2 * inch))

        # User Info
        elements.append(Paragraph(f"User: {request.user.username}", normal_style))
        elements.append(Paragraph(f"Email: {request.user.email}", normal_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y')}", normal_style))
        elements.append(Spacer(1, 0.3 * inch))

        # Budget Overview
        elements.append(Paragraph("Budget Overview", styles['Heading2']))
        overview_data = [
            ['Total Income', f"₹{budget.total_income}"],
            ['Total Budgeted', f"₹{budget.total_budgeted}"],
            ['Total Spent', f"₹{budget.total_spent}"],
            ['Status', 'Overspent' if budget.total_spent > budget.total_budgeted else 'Fully Spent' if budget.total_spent == budget.total_budgeted else 'Within Budget']
        ]
        overview_table = Table(overview_data, colWidths=[2 * inch, 4 * inch])
        overview_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
        ]))
        elements.append(overview_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Categories Table
        elements.append(Paragraph("Categories", styles['Heading2']))
        category_data = [['Category', 'Limit', 'Spent', 'Remaining', 'Status']]
        for category in categories_data:
            status = 'Overspent' if category['spent'] > category['limit'] else 'Fully Spent' if category['spent'] == category['limit'] else 'Within Budget'
            category_data.append([
                category['name'],
                f"₹{category['limit']}",
                f"₹{category['spent']}",
                f"₹{category['remaining']}",
                status
            ])
        category_table = Table(category_data, colWidths=[1.5 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch, 1.4 * inch])
        category_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
        ]))
        elements.append(category_table)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{budget.month}_budget_summary.pdf"'
        buffer.close()
        return response
    except Budget.DoesNotExist:
        raise Http404("Budget not found.")
    
@login_required
def emi_calculator(request):
    emi_result = None
    if request.method == 'POST':
        try:
            principal = float(request.POST.get('principal'))
            interest_rate = float(request.POST.get('interest_rate'))
            tenure_years = int(request.POST.get('tenure'))

            # Convert to monthly values
            monthly_rate = interest_rate / (12 * 100)  # Annual rate to monthly decimal
            tenure_months = tenure_years * 12

            # EMI formula: [P * r * (1+r)^n] / [(1+r)^n - 1]
            emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / ((1 + monthly_rate) ** tenure_months - 1)
            total_payment = emi * tenure_months
            total_interest = total_payment - principal

            emi_result = {
                'emi': round(emi, 2),
                'total_interest': round(total_interest, 2),
                'total_payment': round(total_payment, 2)
            }
        except (ValueError, ZeroDivisionError):
            messages.error(request, 'Invalid input. Please check your values.')
            return redirect('emi_calculator')

    return render(request, 'features/emi_calculator.html', {'emi_result': emi_result})

@login_required
def experts_list(request):
    if request.user.profile.role != 'NormalUser':
        messages.error(request, 'Only normal users can book experts.')
        return redirect('budget_list')
    experts = ExpertProfile.objects.all()
    return render(request, 'experts/experts_list.html', {'experts': experts})

@login_required
def book_expert(request, expert_id):
    if request.user.profile.role != 'NormalUser':
        messages.error(request, 'Only normal users can book experts.')
        return redirect('budget_list')
    try:
        expert = ExpertProfile.objects.get(user__id=expert_id)
        if request.method == 'POST':
            date_time_str = request.POST.get('date_time')
            try:
                date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')
                if date_time < timezone.now().replace(tzinfo=None):
                    messages.error(request, 'Cannot book a session in the past.')
                    return redirect('book_expert', expert_id=expert_id)
                booking = Booking.objects.create(
                    user=request.user,
                    expert=expert.user,
                    date_time=date_time,
                    status='Pending'
                )
                Notification.objects.create(
                    booking=booking,
                    sender=request.user,
                    recipient=expert.user,
                    message=f"Booking request for {date_time.strftime('%d %B %Y, %H:%M')} from {request.user.username}"
                )
                messages.success(request, 'Booking request submitted successfully!')
                return redirect('booking_history')
            except ValueError:
                messages.error(request, 'Invalid date or time format.')
                return redirect('book_expert', expert_id=expert_id)
        return render(request, 'experts/book_expert.html', {'expert': expert})
    except ExpertProfile.DoesNotExist:
        raise Http404("Expert not found.")

@login_required
def booking_details(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        if request.user != booking.user and request.user != booking.expert and request.user.profile.role != 'Admin':
            raise Http404("You don't have permission to view this booking.")
        return render(request, 'experts/booking_details.html', {'booking': booking})
    except Booking.DoesNotExist:
        raise Http404("Booking not found.")

@login_required
def submit_feedback(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user, status='Completed')
        if Feedback.objects.filter(booking=booking).exists():
            messages.error(request, 'Feedback already submitted.')
            return redirect('booking_details', booking_id=booking_id)
        if request.method == 'POST':
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    raise ValueError
                Feedback.objects.create(
                    booking=booking,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, 'Feedback submitted successfully!')
                return redirect('booking_details', booking_id=booking_id)
            except ValueError:
                messages.error(request, 'Invalid rating. Please select a value between 1 and 5.')
                return redirect('submit_feedback', booking_id=booking_id)
        return render(request, 'experts/feedback_form.html', {'booking': booking})
    except Booking.DoesNotExist:
        raise Http404("Booking not found or not eligible for feedback.")

@login_required
def booking_history(request):
    if request.user.profile.role == 'NormalUser':
        bookings = Booking.objects.filter(user=request.user).order_by('-date_time')
    elif request.user.profile.role == 'FinanceExpert':
        bookings = Booking.objects.filter(expert=request.user).order_by('-date_time')
    else:
        messages.error(request, 'You do not have access to booking history.')
        return redirect('budget_list')
    return render(request, 'experts/booking_history.html', {'bookings': bookings})

@login_required
def experts_appointments(request):
    if request.user.profile.role != 'FinanceExpert':
        messages.error(request, 'Only experts can view appointments.')
        return redirect('budget_list')
    appointments = Booking.objects.filter(expert=request.user, status='Pending').order_by('date_time')
    return render(request, 'experts/experts_appointments.html', {'appointments': appointments})

@login_required
def update_booking_status(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, expert=request.user)
        if request.method == 'POST':
            status = request.POST.get('status')
            if status in ['Pending', 'Confirmed', 'Completed', 'Cancelled']:
                booking.status = status
                booking.save()
                Notification.objects.create(
                    booking=booking,
                    sender=request.user,
                    recipient=booking.user,
                    message=f"Booking status updated to {status} for {booking.date_time.strftime('%d %B %Y, %H:%M')}"
                )
                messages.success(request, 'Booking status updated successfully!')
            else:
                messages.error(request, 'Invalid status.')
            return redirect('booking_details', booking_id=booking_id)
        raise Http404("Invalid request.")
    except Booking.DoesNotExist:
        raise Http404("Booking not found.")

@login_required
def send_notification(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, expert=request.user)
        if request.method == 'POST':
            message = request.POST.get('message')
            if message:
                Notification.objects.create(
                    booking=booking,
                    sender=request.user,
                    recipient=booking.user,
                    message=message
                )
                messages.success(request, 'Notification sent successfully!')
            else:
                messages.error(request, 'Message cannot be empty.')
            return redirect('booking_details', booking_id=booking_id)
        raise Http404("Invalid request.")
    except Booking.DoesNotExist:
        raise Http404("Booking not found.")
    
@login_required
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'features/notifications.html', {'notifications': notifications})

@login_required
def user_management(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, 'Only company Admin can access user management.')
        return redirect('dashboard')
    users = User.objects.select_related('profile').all()
    return render(request, 'admin/user_management.html', {'users': users})

@login_required
def toggle_user_status(request, user_id):
    if request.user.profile.role != 'Admin':
        messages.error(request, 'Only Admin can modify user status.')
        return redirect('dashboard')
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'Cannot modify your own status.')
        return redirect('user_management')
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f'User {user.username} {"activated" if user.is_active else "deactivated"} successfully.')
    return redirect('user_management')

@login_required
def experts_history(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, 'Only company Admin can access expert booking history.')
        return redirect('budget_list')
    bookings = Booking.objects.select_related('user', 'expert', 'expert__profile').order_by('-date_time')
    return render(request, 'admin/experts_history.html', {'bookings': bookings})

@login_required
def company_transaction_management(request):
    if request.user.profile.role != 'CompanyStaff':
        messages.error(request, 'Only company staff can access transaction management.')
        return redirect('dashboard')
    
    current_month = timezone.now().strftime('%B %Y')
    month_filter = request.GET.get('month', current_month)
    category_filter = request.GET.get('category', '')
    
    transactions = CompanyTransaction.objects.filter(month=month_filter)
    if category_filter:
        transactions = transactions.filter(category=category_filter)
    
    categories = CompanyTransaction.objects.values('category').distinct().order_by('category')
    
    if request.method == 'POST':
        type = request.POST.get('type')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        payee_payer = request.POST.get('payee_payer')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        month = request.POST.get('month', current_month)
        
        try:
            amount = float(amount)
            date = datetime.strptime(date, '%Y-%m-%d').date()
            CompanyTransaction.objects.create(
                created_by=request.user,
                type=type,
                amount=amount,
                date=date,
                payee_payer=payee_payer,
                month=month,
                category=category,
                description=description
            )
            messages.success(request, 'Transaction added successfully.')
            return redirect('company_transaction')
        except ValueError:
            messages.error(request, 'Invalid amount or date format.')
    
    total_income = transactions.filter(type='Incoming').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = transactions.filter(type='Outgoing').aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expenses
    
    transaction_data = {
        'labels': ['Income', 'Expenses'],
        'data': [float(total_income), float(total_expenses)]
    }
    # distinct_months = CompanyTransaction.objects.values('month').distinct().order_by('-date')

    distinct_months = (
        CompanyTransaction.objects
        .annotate(months=TruncMonth('date'))
        .values('month')
        .distinct()
        .order_by('-month')
    )

    # formatted_months = [m['month'].strftime('%B %Y') for m in distinct_months]
    
    context = {
        'transactions': transactions.order_by('-date'),
        'distinct_months': distinct_months ,
        'categories': [c['category'] for c in categories if c['category']],
        'month_filter': month_filter,
        'category_filter': category_filter,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
        'transaction_data': json.dumps(transaction_data, default=str)
    }
    return render(request, 'staff/company_transaction.html', context)

@login_required
def transaction_summary(request, month):
    if request.user.profile.role != 'CompanyStaff':
        messages.error(request, 'Only company staff can access transaction summary.')
        return redirect('dashboard')
    
    transactions = CompanyTransaction.objects.filter(month=month).order_by('-date')
    total_income = transactions.filter(type='Incoming').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = transactions.filter(type='Outgoing').aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expenses
    
    transaction_data = {
        'labels': ['Income', 'Expenses'],
        'data': [float(total_income), float(total_expenses)]
    }
    
    context = {
        'month': month,
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
        'transaction_data': json.dumps(transaction_data, default=str)
    }
    
    if 'export' in request.GET:
        export_type = request.GET.get('export')
        if export_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="transaction_summary_{month}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Date', 'Type', 'Payee/Payer', 'Category', 'Amount', 'Description'])
            for t in transactions:
                writer.writerow([t.date, t.type, t.payee_payer, t.category, t.amount, t.description])
            writer.writerow([])
            writer.writerow(['Total Income', '', '', '', total_income, ''])
            writer.writerow(['Total Expenses', '', '', '', total_expenses, ''])
            writer.writerow(['Net Balance', '', '', '', net_balance, ''])
            return response
        
        elif export_type == 'pdf':
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=30, bottomMargin=30)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontName='Helvetica-Bold',
                fontSize=16,
                textColor=colors.darkblue,
                spaceAfter=20,
                alignment=1  # Center
            )
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10,
                textColor=colors.black,
                spaceAfter=10
            )
            
            # Header
            elements.append(Paragraph(f"Transaction Summary - {month}", title_style))
            elements.append(Spacer(1, 12))
            
            # Transaction Table
            data = [['Date', 'Type', 'Payee/Payer', 'Category', 'Amount', 'Description']]
            for t in transactions:
                data.append([
                    t.date.strftime('%Y-%m-%d'),
                    t.type,
                    t.payee_payer,
                    t.category,
                    f"{t.amount:,.2f}",
                    t.description[:50]
                ])
            
            table = Table(data, colWidths=[80, 80, 120, 100, 80, 150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            # Summary Section
            elements.append(Paragraph(f"Total Income: INR {total_income:,.2f}", normal_style))
            elements.append(Paragraph(f"Total Expenses: INR {total_expenses:,.2f}", normal_style))
            elements.append(Paragraph(f"Net Balance: INR {net_balance:,.2f}", normal_style))
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="transaction_summary_{month}.pdf"'
            return response
    
    return render(request, 'staff/transaction_summary.html', context)

@login_required
def user_budget_history(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, 'Only Admin can export user budget history.')
        return redirect('dashboard')
    
    users = Profile.objects.filter(role='NormalUser').select_related('user')
    user_data = []
    for profile in users:
        budgets = Budget.objects.filter(user=profile.user).order_by('-month')
        total_budgets = budgets.count()
        total_budgeted = budgets.aggregate(total=Sum('total_budgeted'))['total'] or 0
        total_expenses = Expense.objects.filter(category__budget__user=profile.user).aggregate(total=Sum('amount'))['total'] or 0
        user_data.append({
            'username': profile.user.username,
            'user_id': profile.user.id,
            'total_budgets': total_budgets,
            'total_budgeted': float(total_budgeted),
            'total_expenses': float(total_expenses),
            'remaining': float(total_budgeted - total_expenses)
        })
    
    context = {'users': user_data}
    return render(request, 'admin/user_budget_history.html', context)

@login_required
def user_budget_detail(request, user_id):
    if request.user.profile.role != 'Admin':
        messages.error(request, 'Only Admin can export user budget history.')
        return redirect('dashboard')
    
    budgets = Budget.objects.filter(user_id=user_id).order_by('-month')
    budget_data = []
    for budget in budgets:
        total_expenses = Expense.objects.filter(category__budget=budget).aggregate(total=Sum('amount'))['total'] or 0
        budget_data.append({
            'id': budget.id,
            'month': budget.month,
            'total_budgeted': float(budget.total_budgeted),
            'total_expenses': float(total_expenses),
            'remaining': float(budget.total_budgeted - total_expenses)
        })
    
    context = {
        'budgets': budget_data,
        'user_id': user_id,
        'username': budgets[0].user.username if budgets else 'Unknown'
    }
    return render(request, 'admin/user_budget_detail.html', context)

@login_required
def export_user_budget_detail_pdf(request, user_id):
    if request.user.profile.role != 'Admin':
        messages.error(request, 'Only Admin can export user budget history.')
        return redirect('dashboard')
    
    budgets = Budget.objects.filter(user_id=user_id).order_by('-month')
    username = budgets[0].user.username if budgets else 'Unknown'
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=30, bottomMargin=30)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=20,
        alignment=1
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.black,
        spaceAfter=10
    )
    
    # Header
    elements.append(Paragraph(f"Budget History for {username}", title_style))
    elements.append(Spacer(1, 12))
    
    # Budget Table
    data = [['Month', 'Total Budgeted', 'Total Expenses', 'Remaining']]
    for budget in budgets:
        total_expenses = Expense.objects.filter(category__budget=budget).aggregate(total=Sum('amount'))['total'] or 0
        data.append([
            budget.month,
            f"₹{budget.total_budgeted:,.2f}",
            f"₹{total_expenses:,.2f}",
            f"₹{budget.total_budgeted - total_expenses:,.2f}"
        ])
    
    table = Table(data, colWidths=[150, 120, 120, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="budget_history_{username}.pdf"'
    return response

@login_required
def company_budget_history(request):
    if request.user.profile.role != 'Admin':
        messages.error(request, 'Only Admin can export user budget history.')
        return redirect('dashboard')
    
    staff = Profile.objects.filter(role='CompanyStaff').select_related('user')
    staff_data = []
    for profile in staff:
        transactions = CompanyTransaction.objects.filter(created_by=profile.user)
        total_transactions = transactions.count()
        total_income = transactions.filter(type='Incoming').aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = transactions.filter(type='Outgoing').aggregate(total=Sum('amount'))['total'] or 0
        staff_data.append({
            'username': profile.user.username,
            'user_id': profile.user.id,
            'total_transactions': total_transactions,
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'net_balance': float(total_income - total_expenses)
        })
    
    context = {'staff': staff_data}
    return render(request, 'admin/company_budget_history.html', context)

@login_required
def company_budget_detail(request, user_id):
    if request.user.profile.role != 'Admin':
        messages.error(request, 'Only Admin can export user budget history.')
        return redirect('dashboard')
    
    transactions = CompanyTransaction.objects.filter(created_by_id=user_id).order_by('-date')
    budget_data = []
    for transaction in transactions:
        budget_data.append({
            'date': transaction.date.strftime('%Y-%m-%d'),
            'type': transaction.type,
            'payee_payer': transaction.payee_payer,
            'category': transaction.category,
            'amount': float(transaction.amount),
            'description': transaction.description[:50]
        })
    
    context = {
        'transactions': budget_data,
        'user_id': user_id,
        'username': transactions[0].created_by.username if transactions else 'Unknown'
    }
    return render(request, 'admin/company_budget_detail.html', context)

@login_required
def export_company_budget_detail_pdf(request, user_id):
    if request.user.profile.role != 'Admin':
        messages.error(request, 'Only Admin can export user budget history.')
        return redirect('dashboard')
    
    transactions = CompanyTransaction.objects.filter(created_by_id=user_id).order_by('-date')
    username = transactions[0].created_by.username if transactions else 'Unknown'
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=30, bottomMargin=30)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=20,
        alignment=1
    )
    
    # Header
    elements.append(Paragraph(f"Company Budget History for {username}", title_style))
    elements.append(Spacer(1, 12))
    
    # Transaction Table
    data = [['Date', 'Type', 'Payee/Payer', 'Category', 'Amount', 'Description']]
    for t in transactions:
        data.append([
            t.date.strftime('%Y-%m-%d'),
            t.type,
            t.payee_payer,
            t.category,
            f"₹{t.amount:,.2f}",
            t.description[:50]
        ])
    
    table = Table(data, colWidths=[80, 80, 120, 100, 80, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="company_budget_history_{username}.pdf"'
    return response