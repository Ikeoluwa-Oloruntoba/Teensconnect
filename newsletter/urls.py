from django.urls import path

from . import views

app_name = 'newsletter'

urlpatterns = [
    path('newsletter/', views.newsletter_signup, name='newsletter')
]