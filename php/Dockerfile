FROM php:7.2.0-apache-stretch

# RUN apt-get install -y apache2-ssl-dev
RUN docker-php-ext-install mysqli
RUN docker-php-ext-install opcache

# COPY php.ini /usr/local/etc/php/
COPY apache2.conf /etc/apache2/apache2.conf
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
COPY app /var/www/html/

EXPOSE 80
EXPOSE 443
