from django import forms
from .models import Trip, Expense
from django.contrib.auth.models import User

class ExpenseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        trip = kwargs.pop('trip', None)
        super().__init__(*args, **kwargs)
        if trip:
            self.fields['paid_by'].queryset = trip.participants.all()
            self.fields['split_with'].queryset = trip.participants.all()

    class Meta:
        model = Expense
        fields = ['description', 'amount', 'category', 'date', 'paid_by', 'split_with', 'receipt_image']
        labels = {
            'description': 'توضیحات',
            'amount': 'مبلغ',
            'category': 'دسته‌بندی',
            'date': 'تاریخ',
            'paid_by': 'پرداخت شده توسط',
            'split_with': 'تقسیم با',
            'receipt_image': 'تصویر رسید',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'split_with': forms.CheckboxSelectMultiple,
        }

class AddParticipantForm(forms.Form):
    email = forms.EmailField(label="ایمیل کاربر")

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("کاربری با این ایمیل یافت نشد.")
        return email

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['name', 'description']
        labels = {
            'name': 'نام سفر',
            'description': 'توضیحات',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
