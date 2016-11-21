from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import HttpResponseRedirect

from . import forms
from .imports import import_csv_becarios, import_csv_centros_plazas

# Create your views here.

class UploadView(TemplateView):
    template_name = 'upload/upload.html'

def upload_becarios(request):
    if request.method == 'POST':
        form = forms.UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                import_csv_becarios(request.FILES['csv_file_field'])
            except ValidationError as e:
                for error in e.error_list:
                    messages.error(request, error)
                return HttpResponseRedirect('/upload/becarios')
            return HttpResponseRedirect('/upload')
    else:
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_becarios.html', {'form': form})

def upload_centros_plazas(request):
    if request.method == 'POST':
        form = forms.UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                import_csv_centros_plazas(request.FILES['csv_file_field'])
            except ValidationError as e:
                for error in e.error_list:
                    messages.error(request, error)
                return HttpResponseRedirect('/upload/plazas')
            return HttpResponseRedirect('/upload')
    else:
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_plazas.html', {'form': form})
