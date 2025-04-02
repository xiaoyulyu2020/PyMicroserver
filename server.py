from flask import Flask, request
# In order instal flask_mysqldb you need  :brew install mysql pkg-config
from flask_mysqldb import MySQL
import jwt, os, datetime

# init server
# connect server to database

server = Flask(__name__)
mysql = MySQL(server)

# Config DB
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")
"""
Some problems may raise:
    1. fail to run: mysql -u root.
        a. Need to run Mysql server first
    2. fail to run: mysql -u root < init.sql
        a. SELECT user, host FROM mysql.user WHERE user = 'auth_user';
            if there is auth_user, then drop it
            DROP USER IF EXISTS 'auth_user'@'localhost';
"""

@server.route("/login", methods=["POST"])
def login():
    """
        Run Mysql server: brew services start mysql
    """
    auth = request.authorization
    if not auth:
        return "No authorization", 401
    cursor = mysql.connection.cursor()
    cursor.execute(

    )