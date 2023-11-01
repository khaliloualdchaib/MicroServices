from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests
import json
parser = reqparse.RequestParser()
parser.add_argument('count')
parser.add_argument('description')

app = Flask("activities")
api = Api(app)
conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="activities", user="postgres", password="postgres", host="activities_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def add_activity(username, description):
    response = requests.get("http://authentication:5000/authentication/" +  username)
    user_exists = True
    if response.status_code == 200:
        user_exists = response.json()["data"]
    if not user_exists:
        return False
    cur = conn.cursor()
    cur.execute("INSERT INTO activities (username, description) VALUES (%s, %s);", (username, description))
    conn.commit()
    return True
def all_activities():
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities;")
    return cur.fetchall()

def get_user_activities(username, n):
    user_exists = True
    response = requests.get("http://authentication:5000/authentication/" +  username)
    if response.status_code == 200:
        user_exists = response.json()["data"]
    if not user_exists:
        return []
    response = requests.get("http://friends:5000/friends/" + username)
    if response.status_code == 200:
        friends = response.json()["data"] #list of friends
        query = """
            SELECT username, description, time
            FROM activities
            WHERE username IN %s
            ORDER BY time DESC;
        """
        cursor = conn.cursor()
        cursor.execute(query, (tuple(friends),))
        results = cursor.fetchall()
        results = [(time.strftime('%Y-%m-%d %H:%M:%S'), username, description) for username, description, time in results]
        results = results[:int(n)]
        return results
    return []
class Activity(Resource):
    def get(self):
        try:
            result = all_activities()
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
        
class UserActivity(Resource):
    def post(self, username):
        args = flask_request.args
        try:
            result = add_activity(username, args['description'])
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
    def get(self, username):
        try:
            args = flask_request.args
            result = get_user_activities(username, args['count'])
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
api.add_resource(Activity, '/activities')
api.add_resource(UserActivity, '/activities/<string:username>')