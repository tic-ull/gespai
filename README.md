# Aplicación para la gestión de los becarios de aulas de informática de la Universidad de La Laguna

__Issues:__ https://github.com/srodmar/gespai/issues


## Requisitos

* [Python 2.7](https://www.python.org/)
* [Django 1.10](https://www.djangoproject.com/)
* [django-notifications](https://github.com/django-notifications/django-notifications)
  * Plugin de Django utilizado para mostrar las notificaciones de la aplicación

### Requisitos para la ejecución en un servidor

  * [Apache 2.4.7](https://httpd.apache.org/)
  * [MySQL 5.5](https://www.mysql.com/)

  #### Configuración de MySQL
  Se debe especificar la dirección de un fichero .cnf en el diccionario DATABASES del fichero [settings.py](https://github.com/srodmar/gespai/blob/apache/gespai/settings.py), que contendrá la configuración de la Base de Datos siguiendo el siguiente formato:

  ```
  [client]
  database = nombre_de_la_bd
  host = localhost
  user = usuario_con_acceso_a_bd
  password = contraseña
  default-character-set = utf8
  ```

  * MySQL-python:

     Paquete necesario para la conexión de Django con la base de datos MySQL. A su vez requiere los siguientes paquetes:

     * libmysqlclient-dev
     * python-dev


  * [mod_wsgi](https://modwsgi.readthedocs.io/en/develop/installation.html):

    Módulo de Apache que permite hostear la aplicación. Requiere el siguiente paquete:

    * apache2-dev

  #### Configuración de Apache

  Configuración extra a añadir al fichero apache2.conf, en la que se indica a Apache la dirección de la aplicación a cargar y donde buscar los ficheros estáticos.

  ```
  WSGIScriptAlias / /path/to/gespai/gespai/wsgi.py
  WSGIPythonPath /path/to/gespai

  <Directory /path/to/gespai/gespai>
  <Files wsgi.py>
  Require all granted
  </Files>
  </Directory>

  Alias /static/ /path/to/gespai/static/
  <Directory /path/to/gespai/static>
  Require all granted
  </Directory>
  ```

  **Nota**: es necesario ejecutar el siguiente comando para que Django mueva los ficheros estáticos al directorio donde los buscará Apache:

  `python manage.py collectstatic`

  (Desde el directorio base del proyecto)

  ___

  La configuración del proyecto para su funcionamiento con Apache y MySQL se encuentra en la rama [apache](https://github.com/srodmar/gespai/tree/apache).

## Acceso a la aplicación

La aplicación se encuentra actualmente desplegada en un servidor del servicio IaaS de la ULL. Puede acceder a la misma en el siguiente [enlace](http://10.6.128.3/), desde la red de la ULL.
