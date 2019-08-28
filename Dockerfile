FROM tiangolo/uwsgi-nginx:python3.7

ENV UWSGI_INI /app/config/nginx/uwsgi.ini
ENV PYTHONUNBUFFERED 1
ENV ENV local

RUN mkdir -p /app/
WORKDIR /app

ADD ./requirements.txt /app/requirements.txt
RUN pip install -U pip
RUN pip install -r /app/requirements.txt

RUN mkdir -p /app/media/
ADD ./manage.py /app/manage.py
ADD ./cert /app/cert/
ADD ./config/ /app/config/
ADD ./scripts/ /app/scripts/
ADD ./adsrental/ /app/adsrental/
ADD ./restapi/ /app/restapi/
ADD ./config/nginx/web.conf /etc/nginx/conf.d/nginx.conf
ADD ./config/nginx/nginx.conf /app/nginx.conf

RUN ln -sf /app/scripts/prestart.sh /app/prestart.sh
ENV UWSGI_CHEAPER 4
ENV UWSGI_PROCESSES 64
ENV NGINX_MAX_UPLOAD 1m
ENV NGINX_WORKER_PROCESSES auto
ENV NGINX_WORKER_CONNECTIONS 8192
ENV NGINX_WORKER_OPEN_FILES 2048

EXPOSE 80
EXPOSE 443
