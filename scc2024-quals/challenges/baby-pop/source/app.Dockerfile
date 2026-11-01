FROM php:7.4-apache

# Set the working directory
WORKDIR /var/www/html

# Copy application source code
COPY src/ .

# Install required dependencies
RUN apt-get update && \
    apt-get install -y libpng-dev && \
    docker-php-ext-install mysqli pdo_mysql && \
    docker-php-ext-enable mysqli pdo_mysql && \
    rm -rf /var/lib/apt/lists/*

CMD ["apache2-foreground"]
