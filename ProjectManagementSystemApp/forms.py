from .models import *
from django import forms
from django.forms import ModelForm

class TeamForm(ModelForm):

    class Meta:
        model = Team
        fields = ['name', 'description', 'managerID']
