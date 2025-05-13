from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = (
        ('NormalUser', 'Normal User'),
        ('CompanyStaff', 'Company Staff'),
        ('FinanceExpert', 'Finance Expert'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"

class BudgetCategory(models.Model):
    budget = models.ForeignKey(Budget, related_name='categories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.allocated_amount})"
    
class Expense(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    name = models.CharField(max_length=255) 
    amount = models.DecimalField(max_digits=10, decimal_places=2) 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.name} - {self.amount}"

class EMIRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.FloatField()
    tenure_months = models.IntegerField()
    calculated_emi = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EMI for {self.user.username} - ₹{self.calculated_emi}/month"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"₹{self.amount} - {self.category} on {self.date}"

class FinanceExpertProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255)
    bio = models.TextField()

    def __str__(self):
        return f"Expert: {self.user.username} - {self.specialization}"

class AppointmentSlot(models.Model):
    expert = models.ForeignKey(FinanceExpertProfile, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"Slot for {self.expert.user.username} on {self.date} ({self.start_time} - {self.end_time})"

