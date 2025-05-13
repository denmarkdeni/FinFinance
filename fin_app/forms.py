from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile, Budget, BudgetCategory, EMIRecord, Payment

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            if not user.is_superuser:
                Profile.objects.filter(user=user).update(role=self.cleaned_data['role'])
        return user

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['title', 'total_amount', 'start_date', 'end_date']