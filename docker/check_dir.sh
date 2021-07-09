#!/bin/sh
if [ ! "$(ls -A /var/lib/postgresql/data)" ]; then
  cp -rf /var/lib/postgresql/data1/* /var/lib/postgresql/data
  echo "Docker restore data dir"
  ls -l /var/lib/postgresql/data
else
  echo "Docker do not restore data dir"
  ls -l /var/lib/postgresql/data
fi

chmod 0700 -R /var/lib/postgresql/data
chown -R postgres /var/lib/postgresql/data
