from calendar import different_locale

from flask import Flask, request
# In order install flask_mysqldb you need  :brew install mysql pkg-config
from flask_mysqldb import MySQL
import jwt, os, datetime

# init server
# connect server to database

server = Flask(__name__)
mysql = MySQL(server)

# Config DB
"""
    Advantage setting the environment variables: flexible
    command line: export MYSQL_HOST=localhost, you can set up the host.
    ...
"""
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
    3. Check the auth db:
        USE auth;
        show tables;
        describe user;
        select * from user;
"""

def createJWT(username, secret, authz):
    """
    A function that generates a JWT token.
    """
    jwtToken = jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=24),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )
    return jwtToken

@server.route("/login", methods=["POST"])
def login():
    """
        Run Mysql server: brew services start mysql
    """
    auth = request.authorization
    if not auth:
        return "No authorization", 401

    # Connect from flask to mysql db
    cursor = mysql.connection.cursor()
    res = cursor.execute(
        "SELECT email, password FROM user WHERE email = %s", (auth.username,)# user uses email as username
    )
    if res > 0: # at least one line existing
        user = cursor.fetchone()  # Fetch user details
        email, password = user

        if auth.username != email and auth.password != password:
            return "Invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JEW_SECRET"), True)
    else:
        return "Invalid credentials", 401

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080, debug=True)