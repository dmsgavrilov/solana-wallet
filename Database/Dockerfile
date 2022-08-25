FROM postgres

WORKDIR /docker-entrypoint-initdb.d
COPY ./schema.sql /docker-entrypoint-initdb.d

ENV POSTGRES_PASSWORD=123