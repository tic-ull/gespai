# Aplicación para la gestión de los becarios de aulas de informática de la Universidad de La Laguna

*[Acceso a la aplicación](djangoapps01.osl.ull.es)*.

## Requisitos

### De sistema
* [Python 3.5](https://www.python.org/)

### De Python
Los requisitos pueden ser instalados mediante: `pip install -r requirements.txt`
* [Django 1.11](https://www.djangoproject.com/)
* [django-notifications-hq 1.3](https://github.com/django-notifications/django-notifications)
  * Plugin de Django utilizado para mostrar las notificaciones de la aplicación

## Requisitos de preproducción

Toda la configuración para preproducción se encuentra en la rama [preproduction].

* [Apache 2.4.7](https://httpd.apache.org/)
* [MySQL 5.5](https://www.mysql.com/)

### Configuración de MySQL
Se debe especificar la dirección de un fichero `.cnf` en el diccionario `DATABASES` del fichero [settings.py](https://github.com/jeplasenciap/gespai/blob/preproduction/gespai/settings.py), que contendrá la configuración de la Base de Datos siguiendo el siguiente formato:

```
[client]
database = nombre_de_la_bd
host = localhost
user = usuario_con_acceso_a_bd
password = contraseña
default-character-set = utf8
```

* [mysqlclient](https://github.com/PyMySQL/mysqlclient-python):

    Paquete necesario para la conexión de Django con la base de datos MySQL. A su vez requiere los siguientes paquetes:
    * libmysqlclient-dev
    * python-dev


* [mod_wsgi](https://modwsgi.readthedocs.io/en/develop/installation.html):

    Módulo de Apache que permite hostear la aplicación. Requiere el siguiente paquete:
    * apache2-dev

### Configuración de Apache

**Nota**: es necesario ejecutar el siguiente comando para que Django mueva los ficheros estáticos al directorio donde los buscará Apache: `python manage.py collectstatic`

Para la configuración de apache es necesario haber instalado mod\_wsgi mediante `pip install mod_wsgi` y correr el comando `mod_wsgi-express setup-server` con las opciones que se quiera.

En el fichero `[update_server.sh](https://github.com/jeplasenciap/gespai/blob/preproduction/update_server.sh)` se encuentra el comando con algunas opciones básicas que permiten correrlo sin posterior configuración.

Dicho comando generará un fichero `apachectl` en el directorio especificado por `--server-root`, que inicia el servidor y puede ser activado con `apachectl start`.
