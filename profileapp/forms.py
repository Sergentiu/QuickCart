from django import forms
from django.contrib.auth.models import User
from django_registration.forms import RegistrationForm

class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class CustomRegistrationForm(RegistrationForm):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email