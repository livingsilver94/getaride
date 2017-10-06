from django.contrib.auth.forms import AuthenticationForm
from django.forms.models import inlineformset_factory
from django import forms
from django.core.validators import MinLengthValidator
from .models import PoolingUser, Trip, Step
from users.forms import UserCreationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                                              'class': 'form-control',
                                                              }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 }))


class SearchTrip(forms.Form):
    """
    Pay attention that id fields are meant to be hidden, since we suppose they come from
    an autocomplete AJAX request via an another CharField.
    """
    origin_id = forms.IntegerField()
    destination_id = forms.IntegerField()
    datetime = forms.DateTimeField()


class PoolingUserForm(forms.ModelForm):
    class Meta:
        model = PoolingUser
        # Exclude the one-to-one relation with User
        fields = ['birth_date', 'driving_license', 'cellphone_number']


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['date_origin', 'max_num_passengers']


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['origin', 'destination', 'hour_origin', 'hour_destination', 'max_price']


StepFormSet = inlineformset_factory(parent_model=Trip, model=Step, form=StepForm, can_delete=False, min_num=1, extra=0)


class UserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.Meta.fields:
            self[field_name].field.required = True
        self['password1'].field.validators = [MinLengthValidator(6)]
