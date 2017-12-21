from email.mime.text import MIMEText
import smtplib

from gespai_admin_settings import smtp_server_name, smtp_server_port, \
    direccion_incidencias_stic, direccion_remitente_osl, direccion_siga, \
    smtp_server_user, smtp_server_password


############################################################
#
# Lo siguiente es para enviar el correo de incidencia al
# stic para notificarlos de las altas y bajas para proceder
# a la inclusión de los becarios en el grupo becasiga
#
############################################################
asunto_correo_becasiga = "Solicitud de modificación de grupo 'becasiga' en LDAP institucional" 
texto_correo_becasiga = """
Hola,

Dadas las nuevas incorporaciones realizadas en la lista de becarios, solicito la siguiente modificación en el grupo correspondiente 'becasiga' del LDAP institucional:

- Bajas:
{}

- Altas:
{}

Un saludo.
"""

"""
def enviar_correo_becasiga_ldap():
    texto_correo_becasiga = texto_correo_becasiga.format(lista_niu_bajas.join("\n"),
                                                         lista_niu_altas.join("\n"))
    with smtplib.SMTP(smtp_server_name, smtp_server_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_server_user, smtp_server_password)
        cuerpo_mensaje = "\r\n".join([
            "From: {}".format(direccion_remitente_osl),
            "To: {}".format(direccion_incidencias_stic),
            "Subject: {}".format(asunto_correo_becasiga),
            "",
            texto_correo_becario
        ])
        server.send_email(
            from_addr = direccion_remitente_osl,
            to_addr_list = [direccion_incidencias_stic],
            cc_addr_list = [direccion_siga], 
            subject = asunto_correo_becasiga, 
            message = cuerpo_mensaje)
"""

############################################################
#
# Lo siguiente es para enviar el correo de alta a los
# becarios
#
############################################################
asunto_correo_alta= "Bienvenido/a a la beca de aulas SIGA"
texto_correo_alta= """
Hola,

Te informamos que has sido dado de alta como becario/a de aula de informática.

Para acceder como administrador de los equipos de las aulas SIGA, así como al Wiki de Aulas, debes usar tu alu institucional (alu0100XXXXXX).

Wiki de aulas: https://aulas.ull.es/inicio

En la sección de la Documentación general de la Wiki dispones de toda la información relacionada con la gestión de las aulas: https://aulas.ull.es/documentacion/inicio

En la Wiki, en la sección del centro que has sido asignado/a, añade tu nombre, e-mail institucional (alu0100XXXXXX) y horario en el que estarás disponible en el aula.

También hay disponible un formulario de incidencias mediante el cual debes informarnos de cualquier problema que ocurra en el aula: http://aulas.ull.es/incidencias/

Cualquier duda, nos puedes contactar a siga@osl.ull.es

<b>Importante:</b> No utilices cuentas de correo que no sea la de tu alu institucional.

Un saludo.
"""

def enviar_correo_becario_alta():
    with smtplib.SMTP("localhost") as server:
        server.starttls()
        direccion_becario = "alu0100791327@ull.edu.es" 
        mensaje = MIMEText(texto_correo_alta)
        mensaje["From"] = direccion_remitente_osl
        mensaje["To"] = direccion_becario
        mensaje["Subject"] = asunto_correo_alta
        mensaje.set_encoding("UTF-8")
        server.sendmail(
            from_addr = direccion_remitente_osl,
            to_addrs = [direccion_becario, direccion_siga],
            msg = mensaje.as_string())
