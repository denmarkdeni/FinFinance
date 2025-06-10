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
    path('dashboard/normal/', views.normal_dashboard, name='normal_dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    path('dashboard/expert/', views.expert_dashboard, name='expert_dashboard'),

    path('staff/create-budget/', views.create_budget, name='create_budget'),
    path('staff/view-expenses/', views.view_expenses, name='view_expenses'),
    path('staff/upload-expense/', views.upload_expense, name='upload_expense'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])