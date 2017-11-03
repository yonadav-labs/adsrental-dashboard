FROM python:2.7

ENV PYTHONUNBUFFERED 1
ENV ENV local
RUN mkdir -p /app/scripts/
WORKDIR /app

RUN virtualenv venv
RUN bash -c 'source venv/bin/activate && pip install django==1.11.4'
RUN bash -c 'source venv/bin/activate && pip install django-cors-headers==2.1.0'
RUN bash -c 'source venv/bin/activate && pip install django-storages==1.6.3'
RUN bash -c 'source venv/bin/activate && pip install django-extensions==1.8.0'
RUN bash -c 'source venv/bin/activate && pip install django-smtp-ssl==1.0'
RUN bash -c 'source venv/bin/activate && pip install flake8==3.4.1'
RUN bash -c 'source venv/bin/activate && pip install gunicorn==19.7.1'
RUN bash -c 'source venv/bin/activate && pip install MySQL-Python==1.2.5'
RUN bash -c 'source venv/bin/activate && pip install werkzeug==0.12.2'
RUN bash -c 'source venv/bin/activate && pip install boto==2.48.0'
RUN bash -c 'source venv/bin/activate && pip install whitenoise==4.0b4'


ADD ./manage.py /app/
ADD ./cert /app/cert/
ADD ./config/ /app/config/
ADD ./scripts/ /app/scripts/
ADD ./adsrental/ /app/adsrental/
ADD ./sf_dump/ /app/sf_dump/

EXPOSE 8007
CMD ["/app/scripts/server.sh"]
