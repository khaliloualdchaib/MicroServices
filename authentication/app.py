from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('password')

app = Flask("authentication")
api = Api(app)
conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="authentication", user="postgres", password="postgres", host="authentication_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")
def username_exists(username):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM authentication WHERE username = %s", (username,))
    return bool(cur.fetchone()[0])
def register(username, password):
    if not username_exists(username):
        cur = conn.cursor()
        cur.execute("INSERT INTO authentication (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return True
    return False
def login(username, password):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM authentication WHERE username = %s AND password = %s;", (username, password))
    return bool(cur.fetchone()[0])
class RegisterResource(Resource):
    def post(self):
        try:
            args = flask_request.args
            result = register(args['username'], args['password'])
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
class LoginResource(Resource):
    def post(self):
        try:
            args = flask_request.args
            result = login(args['username'], args['password'])
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
class AuthenticationResource(Resource):
    def get(self, username=None):
        if username is None:
            return {"data": False}, 200
        try:
            result = username_exists(username)
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
api.add_resource(RegisterResource, '/authentication/register')
api.add_resource(LoginResource, '/authentication/login')
api.add_resource(AuthenticationResource, '/authentication/<string:username>')