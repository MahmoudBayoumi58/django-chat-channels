from django.forms import *
from .models import *


class UserCreationForm(ModelForm):
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'password']

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

        return user
