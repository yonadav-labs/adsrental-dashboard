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

ADD ./requirements /app/requirements/
RUN pip install -r /app/requirements/base.txt

RUN apk --no-cache del gcc musl-dev

# ADD ./scripts/install_venv.sh /app/scripts/install_venv.sh
# RUN ./scripts/install_venv.sh

RUN mkdir -p /app/media/
ADD ./manage.py /app/
ADD ./cert /app/cert/
ADD ./config/ /app/config/
ADD ./scripts/ /app/scripts/
ADD ./salesforce_handler/ /app/salesforce_handler/
ADD ./adsrental/ /app/adsrental/
ADD ./sf_dump/ /app/sf_dump/

EXPOSE 8007
CMD ["/app/scripts/server.sh"]
