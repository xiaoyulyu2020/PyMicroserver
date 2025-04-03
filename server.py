import datetime
import jwt
import os
from flask import Flask, request
# In order install flask_mysqldb you need  :brew install mysql pkg-config
from flask_mysqldb import MySQL

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


# work flow: user Login -> create jwt token -> validation

def create_jwt(username, secret, authz):
    """
    A function that generates a JWT token.
    """
    jwt_token = jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=24),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256"
    )
    return jwt_token

def decode_jwt(jwt_token, secret):
    """Verifies and decodes a JWT token."""
    try:
        decoded = jwt.decode(jwt_token, secret, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return "Token expired", 401
    except jwt.InvalidTokenError:
        return "Invalid token", 401

@server.route("/login", methods=["POST"])
def login():
    """
    A function that checks the user input such as username and password. Identify if the user is valid.
    Generate jwt token if valid, reject otherwise.
    """
    auth = request.authorization
    if not auth:
        return "No authorization", 401

    # Connect from flask to mysql db
    cursor = mysql.connection.cursor()
    # Run sql : check db if there are any matches with user inputs. is username existing?
    res = cursor.execute(
        "SELECT email, password FROM user WHERE email = %s", (auth.username,)  # user uses email as username
    )
    if res > 0:  # at least one line existing
        user = cursor.fetchone()  # Fetch user details
        email, password = user

        if auth.username != email and auth.password != password:
            return "Invalid credentials", 401
        else:
            return create_jwt(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "Invalid credentials", 401

@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = None

    # Check if JWT is in JSON body
    if request.is_json and "jwt" in request.json:
        encoded_jwt = request.json["jwt"]
        print("JWT received from JSON body")

    # Check if JWT is in Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):# the header will be like "Bearer token"
        encoded_jwt = auth_header.split(" ")[1]
        print("JWT received from Authorization header")

    if not encoded_jwt:
        return {"message": "No JWT provided"}, 400

    # Verify JWT
    decoded = decode_jwt(encoded_jwt, os.environ.get("JWT_SECRET"))

    if isinstance(decoded, tuple):  # If verification fails, it returns a tuple (message, status)
        return {"message": decoded[0]}, decoded[1]

    return {"message": "Token is valid", "data": decoded}, 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
