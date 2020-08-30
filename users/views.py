from django.shortcuts import render, redirect
from .forms import UserExtraDetailsForm, UserForm, ExperienceForm, EducationForm, AwardForm, SkillForm, PublicationForm, \
    ProjectForm, ContactDetailsForm, ContactForm
from django.contrib.auth.decorators import login_required
from .models import UserExtraDetails, Experience, Education, Award, Skill, Publication, Project, ContactDetails
from django.views.generic.edit import DeleteView
from django.contrib.auth.models import User
from .decorators import unauthenticated_user
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
import os

# Create your views here.
category_name_model_form_dict = {'skill': [Skill, SkillForm, 'Skill', 'skill', SkillForm()], \
                                 'publication': [Publication, PublicationForm, 'Publication', 'publication',
                                                 PublicationForm()], \
                                 'project': [Project, ProjectForm, 'Project', 'project', ProjectForm()], \
                                 'education': [Education, EducationForm, 'Education', "education", EducationForm()],
                                 'experience': [Experience, ExperienceForm, 'Experience', 'experience',
                                                ExperienceForm()],
                                 'contactdetails': [ContactDetails, ContactDetailsForm, 'ContactDetails',
                                                    'contactdetails', ContactDetailsForm()],

                                 'award': [Award, AwardForm, 'Award', 'award', AwardForm()]}


def index(request):
    return render(request, "users/index.html")

def mail(request):
    submitted = False
    if request.method == 'POST':

        person_name = request.POST['person_name']
        email = request.POST['email']
        email_subject = request.POST['email_subject']
        message = request.POST['message']

        sender_subject = "Reply from " + person_name
        to_Admin = "Hello ""TeensConnect"",\n" + " <br>you got contacted by " + person_name + " <br>" + "Message for you is, <strong>" + message + "</strong></br>" + " <br> sender emailid - " + email + "</br>"

        send_mail(email_subject,
                  settings.EMAIL_HOST_USER,
                  message,
                  ['teensconnectafrica@gmail.com'],
                  html_message=to_Admin,
                  fail_silently=False)
    return render(request, 'users/index.html')


def projects(request):
    app_url = "/"
    username = os.getenv('MY_ID')
    user = get_object_or_404(User, username=username)
    projects = Project.objects.all().filter(user_id=user.id).order_by('-project_end_month_year')
    print(app_url, "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", projects)
    return render(request, "users/projects.html",
                  {'userfirstname': user.first_name, 'app_url': app_url, 'projects': projects})


def viewProfile(request, username):
    isAdmin = False
    print("in view Profile", username)
    user = None
    try:
        user = get_object_or_404(User, username=username)
    except:
        raise Http404("User not found")
    exps = Experience.objects.all().filter(user_id=user.id).order_by('-end_month_year')
    skills = Skill.objects.all().filter(user_id=user.id).order_by('-percentage_you_know')
    awards = Award.objects.all().filter(user_id=user.id).order_by('-award_month_year')
    publications = Publication.objects.all().filter(user_id=user.id).order_by('-publication_date')
    projects = Project.objects.all().filter(user_id=user.id).order_by('-project_end_month_year')
    education = Education.objects.all().filter(user_id=user.id).order_by('-college_end_month_year')
    contactdetails = ContactDetails.objects.all().filter(user_id=user.id)
    user_details = User.objects.get(id=user.id)
    user_extra_details = UserExtraDetails.objects.get(user_id=user.id)
    return render(request, "users/userprofile.html",
                  {'userfirstname': user.first_name, 'isAdmin': isAdmin, 'experiences': exps, 'skills': skills,
                   'awards': awards, 'publications': publications, 'projects': projects, 'username': username,
                   'user_details': user_details, 'user_extra_details': user_extra_details, 'education': education,
                   'contactdetails': contactdetails})

def userProjects(request, username):
    user = None
    user_url = "/".join(request.build_absolute_uri().split("/projects/")[:-1])
    try:
        user = get_object_or_404(User, username=username)
    except:
        raise Http404("User not found")

    projects = Project.objects.all().filter(user_id=user.id).order_by('-project_end_month_year')

    # print(app_url,"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    return render(request, "users/projects.html",
                  {'userfirstname': user.first_name, 'app_url': user_url, 'projects': projects})


def convertToCamelCase(word):
    return ' '.join(x.capitalize() or '_' for x in word.split('_'))


@login_required
def editableCategory(request, category, category_id):
    print("in view editableCategory", category, category_id)
    if category in category_name_model_form_dict:
        to_edit = False
        current_user_id = request.user.id
        print(request.user.id)
        user_category_form = category_name_model_form_dict[category][4]
        user_category_data = None
        if request.method == 'POST':
            user_category = None
            if category_id != 'new':
                user_category = category_name_model_form_dict[category][0].objects.filter(user_id=current_user_id,
                                                                                          id=int(category_id))
            if user_category:
                user_category_data = user_category[0]

            if user_category or category_id == 'new':
                user_category_form = category_name_model_form_dict[category][1](request.POST, request.FILES,
                                                                                instance=user_category_data)

                if user_category_form.is_valid():
                    print(user_category_form)

                    obj = user_category_form.save(commit=False)
                    if category_id == 'new':
                        obj.user_id = current_user_id
                    obj.save()
                    return HttpResponseRedirect(reverse("users:category", args=(category_name_model_form_dict[category][3],)))
                else:
                    print(user_category_form.errors)

            else:
                raise Http404("No " + category_name_model_form_dict[category][2] + " found")

        else:
            if category_id != "new":
                to_edit = True
                user_category = category_name_model_form_dict[category][0].objects.filter(user_id=current_user_id,
                                                                                          id=int(category_id))
                if user_category:
                    user_category_data = user_category[0]
                    user_category_form = category_name_model_form_dict[category][1](instance=user_category_data)
                    print(user_category_form)
                else:
                    raise Http404("No " + category_name_model_form_dict[category][2] + " found")

        return render(request, "users/commoneditableform.html", {'form_requested': user_category_form, 'type_of_user_detail':
            category_name_model_form_dict[category][3], 'model_name': category_name_model_form_dict[category][2],
                                                           'isEdit': to_edit})


@login_required
def showCategory(request, category):
    print("inshow category", category)
    if category in category_name_model_form_dict:
        current_user_id = request.user.id
        user_awards = category_name_model_form_dict[category][0].objects.filter(user_id=current_user_id)
        print(user_awards)
        fieldlist = [convertToCamelCase(f.name) for f in category_name_model_form_dict[category][0]._meta.get_fields()
                     if f.name != 'user']
        return render(request, "users/commondisplaypage.html", {'fieldlist': fieldlist, 'user_forms': user_awards,
                                                          'type_of_user_detail':
                                                              category_name_model_form_dict[category][3],
                                                          'model_name': category_name_model_form_dict[category][2]})
    else:
        raise Http404("Page not found")

@login_required
def deleteCategory(request, category, category_id):
    try:
        user_category = get_object_or_404(category_name_model_form_dict[category][0], pk=category_id)
        user_category.delete()
        return HttpResponseRedirect(reverse('users:category', args=(category_name_model_form_dict[category][3],)))
    except:
        raise Http404("No " + category_name_model_form_dict[category][2] + " found")


def sendemail(request, username):  # remaining
    user = None
    if request.method == "POST":
        try:
            user = get_object_or_404(User, username=username)
        except:
            raise Http404("User not found")
        person_name = request.POST['person_name']
        email = request.POST['email']
        email_subject = request.POST['email_subject']
        message = request.POST['message']
        to_sender = "Hello " + person_name + "\n" + "you will be contacted soon. <br>" + "Your Message was, <strong>" + message + "<strong>"
        to_sender_subject = "Reply from " + user.first_name
        to_user = "Hello " + user.first_name + ",\n" + " <br>you got contacted by " + person_name + " <br>" + "Message for you is, <strong>" + message + "</strong></br>" + " <br> sender emailid - " + email + "</br>"

        try:
            send_mail(to_sender_subject,
                      message,
                      settings.EMAIL_HOST_USER,
                      [email],
                      html_message=to_sender,
                      fail_silently=False)
            send_mail(email_subject,
                      message,
                      settings.EMAIL_HOST_USER,
                      [user.email],
                      html_message=to_user,
                      fail_silently=False)

        except Exception as e:
            print(e)
            print("nope")

        return redirect(f'/profile/{username}')

    else:

        return redirect(f'/profile/{username}')


@login_required
def showEditableProfile(request):
    current_user_id = request.user.id

    if request.method == "POST":
        print(request.POST, request.FILES)
        profile = UserExtraDetails.objects.get(user_id=current_user_id)

        form = UserExtraDetailsForm(request.POST, request.FILES, instance=profile)
        user_form = UserForm(data=request.POST, instance=request.user)
        print(user_form.fields.keys())

        if form.is_valid():

            obj = form.save()
            if 'user_resume' not in request.FILES:
                print("user_r not changed", profile.user_resume)
                obj.user_resume = profile.user_resume
            if 'user_image' not in request.FILES:
                print("user_image not changed", profile.user_image)
                obj.user_image = profile.user_image
            obj.save()
            form.initial['user_resume'] = obj.user_resume
            # print (obj.user_resume,obj.user_image)

        if user_form.is_valid() and user_form.changed_data:
            if 'username' in user_form.changed_data and User.objects.filter(
                    username=user_form.cleaned_data['username']).exists():
                messages.info(request, "Username taken")
                return redirect('profile')
            elif 'email' in user_form.changed_data and User.objects.filter(
                    email=user_form.cleaned_data['email']).exists():
                messages.info(request, "Email exists")
                return redirect('profile')
            else:
                print("valid user from")
                user_form.save()

        messages.info(request, "Information Updated")

    print('profile GET')
    current_user_id = request.user.id
    # print(type(current_user_id))
    user_extra_details = UserExtraDetails.objects.get(user_id=current_user_id)
    user_info = User.objects.get(id=current_user_id)

    # print(user_extra_details,type(user_info))
    user_details_form = UserExtraDetailsForm(
        initial={'user_interest': user_extra_details.user_interest, 'user_address': user_extra_details.user_address,
                 'user_project_completed': user_extra_details.user_project_completed,
                 'user_image': user_extra_details.user_image, 'user_resume': user_extra_details.user_resume})
    # print(user_details_form)
    info = user_info.username
    ip = 'teensconnectafrica.com'
    ht = 'http://'
    pro = "/profile/"

    shareable_url = "{}{}{}{}".format(ht, ip, pro, info)

    user_info_form = UserForm(
        initial={'first_name': user_info.first_name, 'last_name': user_info.last_name, 'username': user_info.username,
                 'email': user_info.email})
    return render(request, "users/profile.html", {'user_details_form': user_details_form, 'user_info_form': user_info_form,
                                            'shareable_url': shareable_url})