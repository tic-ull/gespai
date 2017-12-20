from django.views import generic
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from gestion import models

def group_check_responsables(user):
    return user.groups.filter(name="responsableaula").exists()

@method_decorator(user_passes_test(group_check_responsables), name="dispatch")
class BecariosView(generic.ListView):
    model = models.Becario
    template_name = "responsables/becarios.html"

    def get_context_data(self, *args, **kwargs):
        context = super(BecariosView, self).get_context_data(**kwargs)
        correo = self.request.user.username + "@ull.edu.es"
        emplazamiento_responsable = models.ResponsableAula.objects.get(email=correo).emplazamiento
        context["emplazamiento"] = emplazamiento_responsable
        plazas = models.Plaza.objects.filter(emplazamiento=emplazamiento_responsable)
        becarios = models.Becario.objects.filter(plaza_asignada__in=plazas)
        context["becarios"] = becarios
        return context
