FROM mysql

COPY config/db_init/init.sql /docker-entrypoint-initdb.d/

EXPOSE 3306