from django.shortcuts import render
from django.views import generic

from gestion import models

# Create your views here.

class ListBecariosView(generic.ListView):
    template_name = 'cambios/list_becarios.html'
    model = models.Becario    
