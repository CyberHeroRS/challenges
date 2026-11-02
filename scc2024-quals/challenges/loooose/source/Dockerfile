FROM php:7.4-apache

WORKDIR /var/www/html

COPY src/ .

# Debian bullseye packages were moved to archive.debian.org.
RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y libpng-dev

EXPOSE 9050

CMD ["apache2-foreground"]