#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE authentication;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "authentication" <<-EOSQL
    CREATE TABLE authentication(
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        PRIMARY KEY (username)
    );
    COPY authentication (username, password)
    FROM '/docker-entrypoint-initdb.d/authentication.csv'
    DELIMITER ','
    CSV HEADER;
EOSQL
