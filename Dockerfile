FROM alpine
MAINTAINER k0perXD@ya.ru

EXPOSE 80
EXPOSE 443

RUN apk update && apk upgrade

RUN apk add \
            gcc \
            musl-dev \
            python3 \
            py3-pip \
            python3-dev \
            postgresql \
            postgresql-dev \
            openssl \
            nginx
RUN pip3 install \
                 flask\
                 psycopg2 \
                 waitress

#nginx
RUN adduser -D -g 'www' www
RUN rm /etc/nginx/nginx.conf
COPY docker/nginx.conf /etc/nginx/
RUN cd /etc/nginx ; mkdir ssl ; cd ssl ; openssl req -new -x509 -days 1461 -nodes -out cert.pem -keyout cert.key -subj "/C=RU/ST=SPb/L=SPb/O=Global Security/OU=IT Department/CN=test.dmosk.local/CN=test"
RUN nginx -t
RUN chown -R www:www /var/lib/nginx
RUN chown -R www:www /etc/nginx


#postgresql
RUN mkdir /run/postgresql
RUN chown postgres:postgres /run/postgresql/

USER postgres
RUN mkdir /var/lib/postgresql/data
RUN chmod 0700 /var/lib/postgresql/data
RUN initdb -D /var/lib/postgresql/data
RUN rm /var/lib/postgresql/data/postgresql.conf
COPY docker/postgresql.conf /var/lib/postgresql/data
RUN pg_ctl start -D /var/lib/postgresql/data && psql --command="CREATE DATABASE goods WITH OWNER = postgres ENCODING = 'UTF8' CONNECTION LIMIT = -1;"

USER root
RUN mv /var/lib/postgresql/data /var/lib/postgresql/data1/
RUN mkdir /var/lib/postgresql/data
COPY . /app
RUN chmod +x /app/docker/*

CMD sh /app/docker/startscript.sh