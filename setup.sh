#########################################################################
# File Name: setup.sh
# Author: BillCong
# mail: cjcbill@gmail.com
# Created Time: 2020年12月15日 星期二 19时08分54秒
#########################################################################
#!/bin/bash

CSV_PATH=$PWD/stardict.csv
TABLE_NAME=stardict
DATABASE_NAME=skywind_t1
MYSQL_USER=root
MYSQL_PASSWORD=""

# Load stardict.csv to mysql
mysql -u $MYSQL_USER -p $MYSQL_PASSWORD -D $DATABASE_NAME -e \
    "LOAD DATA LOCAL INFILE \"$CSV_PATH\" \
    INTO TABLE $TABLE_NAME                \
    FIELDS TERMINATED BY ','              \
    OPTIONALLY ENCLOSED BY '\"'           \
    LINES TERMINATED BY '\n'              \
    IGNORE 1 LINES;"

echo "export PATH=\"$PWD:\$PATH\"" >> ~/.bashrc
echo "stardict setup finished!"
