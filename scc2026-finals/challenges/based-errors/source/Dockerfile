FROM docker.io/php:8.2-apache

RUN docker-php-ext-install pdo_mysql && docker-php-ext-enable pdo_mysql

# Enable Apache modules for Basic Auth
RUN a2enmod auth_basic authn_file

# Allow .htaccess overrides in /var/www/html
RUN sed -i '/<Directory \/var\/www\/html>/,/<\/Directory>/c\
<Directory /var/www/html>\n\
    Options Indexes FollowSymLinks\n\
    AllowOverride All\n\
    Require all granted\n\
</Directory>' /etc/apache2/sites-available/000-default.conf

COPY ./entrypoint.sh /entrypoint.sh
COPY ./www /var/www/html
COPY .htpasswd /var/www/.htpasswd

RUN chown root:www-data /var/www/.htpasswd && chmod 640 /var/www/.htpasswd

ENTRYPOINT [ "/entrypoint.sh" ]