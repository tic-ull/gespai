from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from gestion import models

from . import forms
from .imports import import_csv_becarios, import_csv_emplazamientos_plazas, import_csv_plan_formacion

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
            errors = import_csv_becarios(request.FILES['csv_file_field'].file)
            if errors:
                for error in errors:
                    error_message = "Error en linea {}: {}".format(str(error[0]), error)
                    messages.error(request, error_message)
                return redirect('/upload/becarios')
            return redirect('/upload')
    else:
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_form.html', {'form': form})


@user_passes_test(group_check)
def upload_emplazamientos_plazas(request):
    if request.method == 'POST':
        form = forms.UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            errors = import_csv_emplazamientos_plazas(request.FILES['csv_file_field'].file)
            if errors:
                for error in errors:
                    error_message = 'Error en linea ' + str(error[0]) + ': '
                    for key, value in error[1].error_dict.items():
                        error_message += key + ': ' + \
                            value[0].messages[0] + ' '
                    messages.error(request, error_message)
                return redirect('/upload/plazas')
            return redirect('/upload')
    else:
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_form.html', {'form': form})


@user_passes_test(group_check)
def upload_plan_formacion(request):
    if request.method == 'POST':
        form = forms.UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            errors = import_csv_plan_formacion(request.FILES['csv_file_field'].file)
            if errors:
                for error in errors:
                    error_message = 'Error en linea ' + str(error[0]) + ': '
                    if isinstance(error[1], models.Becario.DoesNotExist) or isinstance(error[1], models.PlanFormacion.DoesNotExist):
                        error_message += error[1].message
                    else:
                        for key, value in error[1].error_dict.items():
                            error_message += key + ': ' + \
                                value[0].messages[0] + ' '
                    messages.error(request, error_message)
                return redirect('/upload/formacion')
            return redirect('/upload')
    else:
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_form.html', {'form': form})
