from django.forms import ModelForm

from .models import *

class NewsletterUserSignUp(ModelForm):
    class Meta:
        model = NewsletterUser
        fields = ['email']

        def clean_email(self):
            email = self.cleaned_data.get('email')
            return email