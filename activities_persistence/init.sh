#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE activities;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "activities" <<-EOSQL
    CREATE TABLE activities(
        username TEXT NOT NULL,
        description TEXT NOT NULL,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (username, time)
    );
EOSQL
