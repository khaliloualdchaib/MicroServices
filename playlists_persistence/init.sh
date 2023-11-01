#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE playlists;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "playlists" <<-EOSQL
    CREATE TABLE playlists(
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        title TEXT NOT NULL,
        shared_with TEXT[] NOT NULL DEFAULT '{}'
    );
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "playlists" <<-EOSQL
    CREATE TABLE songs(
        artist TEXT NOT NULL,
        title TEXT NOT NULL,
        playlist_id INTEGER NOT NULL,
        PRIMARY KEY (artist, title, playlist_id),
        FOREIGN KEY (playlist_id) REFERENCES playlists (id)
    );
EOSQL