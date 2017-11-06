FROM python:2.7

ENV PYTHONUNBUFFERED 1
ENV ENV local
RUN mkdir -p /app/scripts/
WORKDIR /app

ADD ./requirements /app/requirements/
ADD ./scripts/install_venv.sh /app/scripts/install_venv.sh
RUN ./scripts/install_venv.sh

ADD ./manage.py /app/
ADD ./cert /app/cert/
ADD ./config/ /app/config/
ADD ./scripts/ /app/scripts/
ADD ./adsrental/ /app/adsrental/
ADD ./sf_dump/ /app/sf_dump/

EXPOSE 8007
CMD ["/app/scripts/server.sh"]
