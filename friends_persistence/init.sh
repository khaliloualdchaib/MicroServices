#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE friends;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "friends" <<-EOSQL
    CREATE TABLE friends(
        username TEXT NOT NULL,
        username_friend TEXT NOT NULL,
        PRIMARY KEY (username, username_friend)
    );
EOSQL