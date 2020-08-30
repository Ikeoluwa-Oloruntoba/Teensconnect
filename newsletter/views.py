from django.shortcuts import render
from .forms import *
from .models import *
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template


# Create your views here.
def newsletter_signup(request):
    form = NewsletterUserSignUp(request.POST)

    if form.is_valid():
        instance = form.save(commit=False)
        if NewsletterUser.objects.filter(email=instance.email).exists():
            messages.warning(request, "Your Email Already exists in our data base", "alert alert-warning alert dismissible")
        else:
            instance.save()
            messages.success(request, "Your Email has be submitted to our data base",
                             "alert alert-success alert dismissible")

            subject = "Thank You for subscribing to our Newsletter"
            from_email = settings.EMAIL_HOST_USER
            to_email = instance.email
            with open(settings.BASE_DIR + "/newsletter/templates/newsletter/sign_message.txt") as f:
                signup_message = f.read()
            message = EmailMultiAlternatives(subject,signup_message,from_email,[to_email])
            html_template = get_template("newsletter/sign_message.html").render()
            message.attach_alternative(html_template,"text/html")
            message.send()

    context = {'form':form,}

    return render(request, 'newsletter/index.html', context)
