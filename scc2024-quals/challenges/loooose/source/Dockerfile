FROM php:7.4-apache

WORKDIR /var/www/html

COPY src/ .

RUN apt-get update && \
    apt-get install -y libpng-dev

EXPOSE 9050

CMD ["apache2-foreground"]