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
ADD ./config/nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 443
# CMD ["/app/scripts/server.sh"]
