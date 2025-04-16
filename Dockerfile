FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema y mod_wsgi
RUN apt-get update && \
    apt-get install -y \
        apache2 \
        libapache2-mod-wsgi-py3 \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        pkg-config \
        default-libmysqlclient-dev \
        netcat-openbsd \
        && \
    apt-get clean

# Actualizar pip e instalar requerimientos de Python
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r /code/requirements.txt

# Añadir instalación de mkdocstrings
RUN pip install mkdocstrings

# Configurar directorio de trabajo
WORKDIR /code

# Copiar archivos del proyecto
COPY . /code/

# Habilitar mod_wsgi en Apache
RUN a2enmod wsgi

# Copiar configuración de Apache
RUN cp /code/apache/000-default.conf /etc/apache2/sites-available/000-default.conf

# Exponer el puerto 80
EXPOSE 80

# Copiar y configurar entrypoint
RUN chmod +x /code/scripts/entrypoint.sh
# ENTRYPOINT ["/code/entrypoint.sh"]


CMD ["/code/scripts/entrypoint.sh"]

# Iniciar Apache
# CMD ["apachectl", "-D", "FOREGROUND"]
# CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]