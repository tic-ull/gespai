from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from gestion import models

from . import forms
from .imports import import_csv_becarios, import_csv_emplazamientos_plazas

# Create your views here.

def group_check(user):
    return user.groups.filter(name='osl').exists()


@method_decorator(user_passes_test(group_check), name='dispatch')
class UploadView(TemplateView):
    template_name = 'upload/upload.html'


@user_passes_test(group_check)
def upload_becarios(request):
    if request.method == 'POST':
        form = forms.UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                errors = import_csv_becarios(request.FILES['csv_file_field'].file)
            except ValidationError as e:
                for error in e:
                    messages.error(request, str(error))
                return redirect('/upload/becarios')
            messages.success(request, "El fichero csv se ha subido correctamente y los datos correpondientes actualizados.")
            return redirect('/upload')
    else:
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_form.html', {'form': form})


@user_passes_test(group_check)
def upload_emplazamientos_plazas(request):
    if request.method == 'POST':
        form = forms.UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                errors = import_csv_emplazamientos_plazas(request.FILES['csv_file_field'].file)
            except ValidationError as e:
                for error in e:
                    messages.error(request, str(error))
                return redirect('/upload/plazas')
            messages.success(request, "El fichero csv se ha subido correctamente y los datos correpondientes actualizados.")
            return redirect('/upload')
    else:
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_form.html', {'form': form})
