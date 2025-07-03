"""
URL configuration for FinFinance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# finfinance/urls.py
from django.contrib import admin
from django.urls import path
from fin_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home_view, name='home'),
    path('auth/', views.auth_view, name='auth'),
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'), 
    path('dashboard/normal/', views.normal_user_dashboard, name='normal_dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    path('dashboard/expert/', views.expert_dashboard, name='expert_dashboard'),

    path('dashboard/admin/users/', views.user_management, name='user_management'),
    path('dashboard/admin/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('dashboard/admin/experts/history/', views.experts_history, name='experts_history'),
    path('dashboard/admin/user-budget-history/', views.user_budget_history, name='user_budget_history'),
    path('dashboard/admin/user-budget-detail/<int:user_id>/', views.user_budget_detail, name='user_budget_detail'),
    path('dashboard/admin/user-budget-detail/<int:user_id>/export-pdf/', views.export_user_budget_detail_pdf, name='export_user_budget_detail_pdf'),
    path('dashboard/admin/company-budget-history/', views.company_budget_history, name='company_budget_history'),
    path('dashboard/admin/company-budget-detail/<int:user_id>/', views.company_budget_detail, name='company_budget_detail'),
    path('dashboard/admin/company-budget-detail/<int:user_id>/export-pdf/', views.export_company_budget_detail_pdf, name='export_company_budget_detail_pdf'),

    path('profile/', views.profile, name='profile'),
    path('profile/normal/', views.user_profile, name='user_profile'),
    path('profile/staff/', views.staff_profile, name='staff_profile'),
    path('profile/expert/', views.expert_profile, name='expert_profile'),

    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/create/', views.create_budget, name='create_budget'),
    path('budgets/<int:budget_id>/', views.budget_detail, name='budget_detail'),
    path('budgets/<int:budget_id>/export-pdf/', views.export_budget_pdf, name='export_budget_pdf'),

    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),

    path('features/emi-calculator/', views.emi_calculator, name='emi_calculator'),

    path('experts/', views.experts_list, name='experts_list'),
    path('experts/book/<int:expert_id>/', views.book_expert, name='book_expert'),
    path('experts/appointments/', views.experts_appointments, name='experts_appointments'),

    path('staff/transactions/', views.company_transaction_management, name='company_transaction'),
    path('staff/transactions/summary/<str:month>/', views.transaction_summary, name='transaction_summary'),

    path('bookings/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('bookings/<int:booking_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('bookings/history/', views.booking_history, name='booking_history'),
    path('bookings/<int:booking_id>/update-status/', views.update_booking_status, name='update_booking_status'),
    path('bookings/<int:booking_id>/send-notification/', views.send_notification, name='send_notification'),

    path('notifications/', views.notifications, name='notifications'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)