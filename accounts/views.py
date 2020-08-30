from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from users.models import UserExtraDetails
from .decorators import unauthenticated_user
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from .models import UserToken
from django.conf import settings
from django.core.mail import send_mail
import os


# Create your views here.

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']

        if password2 == password1:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username taken")
                return render(request, "accounts/register.html")
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email exists")
                return render(request, "accounts/register.html")

            else:
                user = User.objects.create_user(username=username, email=email, password=password1,
                                                first_name=first_name, last_name=last_name)
                userdetails = UserExtraDetails(user_id=user.id)
                user.save()
                userdetails.save()
                print("user created")
                return redirect('/login')

        else:
            messages.info(request, "Password dont match")
            return render(request, "accounts/register.html")


    else:
        return render(request, "accounts/register.html")

@unauthenticated_user
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            print("usrr foun3")
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect('/profile')
        else:
            messages.info(request, "Invalid Credentials")
            print("usrr not foun2")
            return redirect('/login')
    else:

        return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    return render(request, 'accounts/logout.html')


def sendMailSendGrid(to_emails, subject, html_content):

    try:
        send_mail(subject,
                  html_content,
                  settings.EMAIL_HOST_USER,
                  [to_emails],
                  fail_silently=False)

        return True
    except Exception as e:
        return False

@unauthenticated_user
def passwordResetEmail(request):
    if request.method == "POST":
        user = None
        try:
            email = request.POST['email']
            user = get_object_or_404(User, email=email)
            unique_id = get_random_string(length=20)
            user_token_object = None
            try:
                user_token_object = UserToken.objects.get(user_id=user.id)
            except:
                print("New reset request")

            if not user_token_object:
                user_token_object = UserToken(user=user, access_token=unique_id)
                user_token_object.save()
            else:
                user_token_object.access_token = unique_id
                user_token_object.save(update_fields=["access_token"])
                info = unique_id
                ip = 'teensconnectafrica.com'
                ht = 'http://'
                pro = "/reset/"

                auth_url = "{}{}{}{}".format(ht, ip, pro, info)

                print(auth_url)
                to_email = email
                subject = "Password Recovery"
                html_content = "This e-mail is in response to your recent request to recover a forgotten password <br/> <br/> <a target='_blank' href=" + auth_url + ">Click here to reset your password</a> <br/> If you are having trouble accessing the link, copy and paste the following link address into your browser window: </br></br>" + auth_url
                if not sendMailSendGrid(to_email, subject, html_content):
                    message = "Please try again later, Email service not working"
                    return render(request, 'accounts/password-reset-done.html', {'message': message})

        except Exception as e:
            print(e)
            print("Error in passwordResetEmail")
        message = "We've emailed you instructions for setting your password, if an account exists with the email(" + email + ") you entered. You should receive them shortly."
        return render(request, 'accounts/password-reset-done.html', {'message': message})

    return render(request, 'accounts/password-reset.html', {'beforeReset': True})

@unauthenticated_user
def passwordResetEmailSent(request):
    message = "We've emailed you instructions for setting your password, if an account exists with the email you entered. You should receive them shortly."
    return render(request, 'accounts/password-reset-done.html', {'message': message})

@unauthenticated_user
def passwordReset(request, token):
    if request.method == 'POST':
        user_token_object = None
        try:
            user_token_object = get_object_or_404(UserToken, access_token=token)
            user = User.objects.get(id=user_token_object.user_id)
            if request.POST['password1'] != request.POST['password2']:
                messages.info(request, "Password don't match")
                return render(request, 'password-reset.html', {'beforeReset': False})
            else:
                user.set_password(request.POST['password1'])
                user.save()
                return redirect('password_reset_done')

        except Exception as e:
            message = "Link Expired"
            return render(request, 'accounts/password-reset-done.html', {'message': message})

    return render(request, 'accounts/password-reset.html', {'beforeReset': False})

@unauthenticated_user
def passwordResetDone(request):
    message = " Your password has been set. You may go ahead and login in"
    return render(request, 'accounts/password-reset-done.html', {'message': message})