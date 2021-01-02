# ECDICT

基于开源项目skywind3000/ECDICT增加查询和快速搭建的方法，支持Linux平台

## 安装步骤

1. 确保环境安装了mysql以及python2.7, python需要安装mysql模块:
```
pip install mysql-python
sudo apt-get install mysql-server
sudo apt-get install libmysqlclient-dev
```
2. 修改/etc/mysql/mysql.conf.d/mysqld.cnf,增加如下内容:
```
[mysqld]
secure-file-priv = ""

[client]  
local_infile=1
```
3. 运行setup.sh将ecdict.csv数据导入mysql数据库, 安装后打开新终端或者source ~/.bashrc。
4. 查询单词时，运行ecd [word],得出读音和解释,需要先修改python文件search中的数据库用户名和密码。

具体介绍可参考原介绍[ECDICT](README-ORIGINAL.md)
