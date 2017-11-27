from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import MinLengthValidator
from django.forms.models import inlineformset_factory
from users.forms import UserCreationForm

from planner.models import PoolingUser, Trip, Step


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                                              'class': 'form-control',
                                                              }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 }))


class CityInput(forms.NumberInput):
    template_name = 'planner/widgets/city.html'

    class Media:
        js = ('planner/js/widgets/city_autocomplete.js',)


class CityField(forms.IntegerField):
    widget = CityInput


class SearchTrip(forms.Form):
    """
    Pay attention that id fields are meant to be hidden, since we suppose they come from
    an autocomplete AJAX request via an another CharField.
    """
    origin = CityField()
    destination = CityField()
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
        widgets = {
            'origin': CityInput(),
            'destination': CityInput(),
            'hour_origin': forms.TimeInput(format='%H:%M'),
            'hour_destination': forms.TimeInput(format='%H:%M'),
        }


StepFormSet = inlineformset_factory(parent_model=Trip, model=Step, form=StepForm, can_delete=False, min_num=1, extra=0,
                                    validate_min=1)


class UserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.Meta.fields:
            self[field_name].field.required = True
        self['password1'].field.validators = [MinLengthValidator(6)]
