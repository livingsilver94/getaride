from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                                            'class': 'form-control',
                                                            }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 }))


class SearchTrip(forms.Form):
    origin_id = forms.IntegerField()
    destination_id = forms.IntegerField()
    datetime = forms.DateTimeField()
