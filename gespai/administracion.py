"""
En este fichero se definen los scripts que ejecutan las tareas de 
administración vinculadas con el manejo de los becarios.

A manera de no mantener información sensible con el repositorio, se carga
la configuración desde un fichero `../../gespai_admin_settings.py`. Se
provee uno solo de ejemplo en el repositorio, mientras que el que va a
ser usado en producción debería ser configurado manualmente.

Para facilitar el proceso puede ser favorable configurar la conexión
por clave.
"""

#from fabric.api import (disconnect_all, env, execute, hide, prompt, puts, run,
#                        settings, sudo, task, warn_only)
from fabric.api import *
from fabric.network import disconnect_all
from .gespai_admin_settings import (ruta_fichero_cas, ruta_fichero_alias_correo,
                                   usuario_conexion, lamp_host, smtp_host)

from gestion.models import Becario, AdministracionEmplazamiento

env.port = "2222"

def dar_alta(correo_alu, plaza):
    """
    Da de alta a un becario en el servidor lamp y smtp especificado,
    modificando los ficheros correspondientes

    Argumentos:
        :correo_alu: El correo del becario, que debe ser de la forma
            "alu\d{10}@ull.edu.es".
        :plaza: El identificador de la plaza en la que se va a dar de
            alta al usuario.
    
    """
    execute(aniadir_en_cas, correo_alu, plaza)
    execute(aniadir_en_correo, correo_alu, plaza)
    execute(actualizar_postfix)
    execute(enviar_correo_alta, correo_alu, plaza)
    disconnect_all()
    

def dar_baja(correo_alu, plaza):
    execute(eliminar_en_cas)
    execute(eliminar_en__correo)
    execute(actualizar_postfix)
    disconnect_all()


def cambiar(correo_alu, plaza_vieja, plaza_nueva):
    execute(eliminar_en_cas)
    execute(aniadir_en_cas)
    execute(eliminar_en_correo)
    execute(aniadir_en__correo)
    execute(actualizar_postfix)
    disconnect_all()


def sanity_check():
    """
    Revisa que la información en los servidores dados esté correcta y
    coincida con la de la base de datos de la aplicación.

    Se pasa por los becarios que estén asignados o hayan renunciado y
    se ve de que todos tengan los permisos correspondientes al día.
    """
    for becario in Becario.objects.filter(Q(estado="A") | Q(estado="R")):
        sanity_check_cas(becario.email, becario.plaza_asignada.emplazamiento.nombre_cas, becario.permisos)
        sanity_check_correo(becario.email, becario.plaza_asignada.emplazamiento.nombre_correo, becario.permisos)


@task
@hosts(lamp_host)
@with_settings(user=usuario_conexion)
def sanity_check_cas(correo_alu, plaza, permisos):
    alu_niu = correo_alu.replace("@ull.edu.es", "")
    try:
        alu_grep = run(r"""grep {} {}""".format(alu_niu, ruta_fichero_cas))
    except:
        return not permisos
    centro_grep = run(r"""grep {} {}""".format(plaza, ruta_fichero_cas))
    alu_grep_count == alu_grep.count(alu_niu)
    return centro_grep == alu_grep and alu_grep_count == 1 and permisos


@task
@hosts(lamp_host)
@with_settings(user=usuario_conexion, warn_only=True)
def aniadir_en_cas(correo_alu, plaza):
    alu = correo_alu.replace("@ull.edu.es", "")
    # Es necesario que el usuario_conexion tenga permisos en la maquina
    sudo(r"""sed -i -r "s/('{}'.*)(\),?\s*$)/\1, '{}'\2/" {}""".format(
        plaza, alu, ruta_fichero_cas))


@task
@hosts(lamp_host)
@with_settings(user=usuario_conexion, warn_only=True)
def eliminar_en_cas(correo_alu, plaza):
    alu = correo_alu.replace("@ull.edu.es", "")
    sudo(r"""sed -i -r "s/{}\s*(, )?//g" {}""".format(alu, ruta_fichero_cas))


@task
@hosts(smtp_host)
@with_settings(user=usuario_conexion, warn_only=True)
def aniadir_en_correo(correo_alu, plaza):
    sudo(r"""sed -r -i "s/({centro}@aulas.ull.es.*)$/\1, {correo_alu}/" {ruta}""".format(correo_alu=correo_alu, centro=plaza, ruta=ruta_fichero_alias_correo))


@task
@hosts(smtp_host)
@with_settings(user=usuario_conexion, warn_only=True)
def eliminar_en_correo(correo_alu, plaza):
    sudo(r"""sed -r -i "s/alu{niu}@ull.edu.es(,?)/\1/" {ruta}""".format(niu=alu_niu, ruta=ruta_fichero_alias_correo))

@task
def enviar_correo_alta(correo_alu, plaza):
    pass


@task
@hosts(smtp_host)
@with_settings(user=usuario_conexion, warn_only=True)
def actualizar_postfix():
        run("postmap /etc/postfix/virtual")
        run("newaliases")
        run("/etc/init.d/postfix reload")
