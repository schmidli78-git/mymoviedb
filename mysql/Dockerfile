FROM mysql:8-oracle

COPY ./dbinit/database.sql /tmp/database.sql
COPY ./dbinit/import_db.sh /docker-entrypoint-initdb.d/
COPY ./dbinit/my.cnf /etc/my.cnf

RUN chown mysql:mysql /tmp/database.sql /docker-entrypoint-initdb.d/* /etc/my.cnf

EXPOSE 3306
