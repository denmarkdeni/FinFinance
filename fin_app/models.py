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
    
# 1. User Profile (Normal Users)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/users/', default='profile_pics/default_user.jpg')
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    financial_goals = models.TextField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - Normal User"

# 2. Staff Profile
class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/staff/', default='profile_pics/default_staff.jpg')
    department = models.CharField(max_length=100, blank=True)
    work_phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} - Staff"

# 3. Finance Expert Profile
class ExpertProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/experts/', default='profile_pics/default_expert.jpg')
    bio = models.TextField(blank=True)
    expertise_area = models.CharField(max_length=100, blank=True)
    consultation_fee = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    available_times = models.CharField(max_length=100, blank=True)
    certificates = models.FileField(upload_to='certificates/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Expert"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)  # e.g. 'June 2025'
    total_income = models.DecimalField(max_digits=10, decimal_places=2)
    total_budgeted = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'month')  # One budget per user per month

    def __str__(self):
        return f"{self.month} Budget for {self.user.username}"

class BudgetCategory(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=50)  # e.g. Food, Rent
    limit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ₹{self.limit}"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"₹{self.amount} on {self.category.name} ({self.date})"
    
class Booking(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bookings')
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expert_bookings')
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.user.username} with {self.expert.username} on {self.date_time}"

class Feedback(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.booking}"
    
class Notification(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification from {self.sender.username} to {self.recipient.username}"