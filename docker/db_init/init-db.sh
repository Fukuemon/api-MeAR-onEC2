#!/bin/bash
set -e

DATABASE=mear
USER=user

DUMP_FILE_PATH=/db-init/mear-db-dump.sql

psql -v ON_ERROR_STOP=1 --username "$USER" --dbname "$DATABASE" <<-EOSQL
    \i '$DUMP_FILE_PATH';
EOSQL
