#########################################################################
# File Name: setup.sh
# Author: BillCong
# mail: cjcbill@gmail.com
# Created Time: 2020年12月15日 星期二 19时08分54秒
#########################################################################
#!/bin/bash

set -x
CSV_PATH=$PWD/dicts/ecdict.csv
TABLE_NAME=ecdict
DATABASE_NAME=skywind_t1
MYSQL_USER=root
MYSQL_PASSWORD=123456

sudo apt-get install mysql-server mysql-client
sudo apt-get install libmysqlclient-dev
pip install MySQL-python
echo "install MySQL-python finished"

if ! mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e "USE $DATABASE_NAME";
then
    mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e \
        "CREATE DATABASE $DATABASE_NAME"
fi

# Create Table
mysql -u $MYSQL_USER -p$MYSQL_PASSWORD --local-infile=1 -D $DATABASE_NAME -e    \
      "CREATE TABLE IF NOT EXISTS $DATABASE_NAME.$TABLE_NAME ( \
      id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,            \
      word VARCHAR(64) NOT NULL UNIQUE KEY,                  \
      sw VARCHAR(64) NOT NULL,                               \
      phonetic VARCHAR(64),                                  \
      definition TEXT,                                       \
      translation TEXT,                                      \
      pos VARCHAR(16),                                       \
      collins SMALLINT DEFAULT 0,                            \
      oxford SMALLINT DEFAULT 0,                             \
      tag VARCHAR(64),                                       \
      bnc INT DEFAULT NULL,                                  \
      frq INT DEFAULT NULL,                                  \
      exchange TEXT,                                         \
      detail TEXT,                                           \
      audio TEXT,                                            \
      KEY(sw, word),                                         \
      KEY(collins),                                          \
      KEY(oxford),                                           \
      KEY(tag)                                               \
      )                                                      \
      ENGINE=MyISAM DEFAULT CHARSET=utf8;"

echo "Mysql Table created!"

mysql -u $MYSQL_USER -p$MYSQL_PASSWORD  -D $DATABASE_NAME -e \
    "set global local_infile = 1;"

# Load stardict.csv to mysql
mysql -u $MYSQL_USER -p$MYSQL_PASSWORD  -D $DATABASE_NAME -e \
    "LOAD DATA LOCAL INFILE \"$CSV_PATH\" \
    INTO TABLE $TABLE_NAME                \
    CHARACTER SET UTF8                    \
    FIELDS TERMINATED BY ','              \
    OPTIONALLY ENCLOSED BY '\"'           \
    LINES TERMINATED BY '\n'              \
    IGNORE 1 LINES;"

echo "Mysql Data loaded!"

echo "export PATH=\"$PWD:\$PATH\"" >> ~/.bashrc
echo "setup.sh finished!"
set +x
