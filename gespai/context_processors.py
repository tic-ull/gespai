#coding=utf-8

# Método que devuelve un diccionario con información que se utilizará
# en las plantillas de la aplicación
def context_processor(request):
    return {
        'is_osl': request.user.groups.filter(name='osl').exists(),
        'is_alu': request.user.groups.filter(name='alumnado').exists(),
        'is_responsable': request.user.groups.filter(name='responsableaula').exists(),
    }
