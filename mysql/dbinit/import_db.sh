#!/bin/bash
mysql -u root -p${MYSQL_ROOT_PASSWORD}< /tmp/database.sql
rm /tmp/database.sql
