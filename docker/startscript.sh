#!/bin/sh
#SSL
cd /etc/nginx/ssl
rm ./*
openssl req -new -x509 -days 1461 -nodes -out cert.pem -keyout cert.key -subj "/C=RU/ST=SPb/L=SPb/O=Global Security/OU=IT Department/CN=test.dmosk.local/CN=test"
cd /

#scripts
sh /app/docker/check_dir.sh
sh /app/docker/postgres_start.sh

#start
nginx
# cd /app && export FLASK_APP=app.py && flask run --no-debugger
cd /app && python3 app.py