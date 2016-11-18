from django.shortcuts import render
from django.views.generic import TemplateView

from . import forms
from .imports import import_csv_becarios

# Create your views here.

class UploadView(TemplateView):
    template_name = 'upload/upload.html'

def upload_becarios(request):
    if request.method == 'POST':
        form = forms.UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            print('el archivo estaba bonito')
            import_csv_becarios(request.FILES['csv_file_field'])
            return HttpResponseRedirect('/')
    else:
        print('else del diablo')
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_becarios.html', {'form': form})
