FROM python:2.7-alpine3.7

ENV PYTHONUNBUFFERED 1
ENV ENV local

RUN mkdir -p /app/
WORKDIR /app

RUN apk --no-cache add \
    gcc \
    musl-dev \
    bash \
    libffi-dev \
    make \
    openssl-dev \
&& echo "Installed build dependencies"

ADD ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN pip install django-admin-caching==0.1.5
RUN pip install django-redis==4.8.0

RUN apk --no-cache del gcc musl-dev

RUN mkdir -p /app/media/
ADD ./manage.py /app/manage.py
ADD ./cert /app/cert/
ADD ./config/ /app/config/
ADD ./scripts/ /app/scripts/
ADD ./adsrental/ /app/adsrental/

EXPOSE 8007
CMD ["/app/scripts/server.sh"]
