from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import PoolingUser


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                                              'class': 'form-control',
                                                              }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 }))


class SearchTrip(forms.Form):
    origin_id = forms.IntegerField()
    destination_id = forms.IntegerField()
    datetime = forms.DateTimeField()


class PoolingUserForm(forms.ModelForm):
    class Meta:
        model = PoolingUser
        # Exclude the one-to-one relation with User
        fields = ['birth_date', 'driving_license']
