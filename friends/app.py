from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests
parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('username_friend')


app = Flask("friends")
api = Api(app)

conn = None
while conn is None:
    try:
        conn = psycopg2.connect(dbname="friends", user="postgres", password="postgres", host="friends_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def get_friends(username):
    user_exists = True
    response = requests.get("http://authentication:5000/authentication/" +  username)
    if response.status_code == 200:
        user_exists = response.json()["data"]
    if user_exists:
        cur = conn.cursor()
        cur.execute("SELECT username_friend FROM friends WHERE username = %s;", (username,))
        friends = [row[0] for row in cur.fetchall()]
        return friends
    return []

def add_friend(username, username_friend):
    friends = get_friends(username)
    response = requests.get("http://authentication:5000/authentication/" +  username)
    user_exists = True
    if response.status_code == 200:
        user_exists = response.json()["data"]
    friend_exists = True
    response = requests.get("http://authentication:5000/authentication/" +  username_friend)
    if response.status_code == 200:
        friend_exists = response.json()["data"]
    if user_exists and friend_exists and username != username_friend and username_friend not in friends:
        cur = conn.cursor()
        cur.execute("INSERT INTO friends (username, username_friend) VALUES (%s, %s);", (username, username_friend))
        conn.commit()
        cur.execute("INSERT INTO friends (username, username_friend) VALUES (%s, %s);", (username_friend, username))
        conn.commit()
        description = "is now friends with " + username_friend
        response = requests.post("http://activities:5000/activities/" +  username + "?description=" + description)
        description = "is now friends with " + username
        
        response = requests.post("http://activities:5000/activities/" +  username_friend + "?description=" + description)
        
        return True
    return False
class GetFriendsResource(Resource):
    def get(self, username=None):
        if username is None:
            return {"data": []}, 200
        try:
            result = get_friends(username)
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500

class AddFriendResource(Resource):
    def post(self):
        try:
            args = flask_request.args
            result = add_friend(args["username"], args["username_friend"])
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
api.add_resource(GetFriendsResource, '/friends/<string:username>', '/friends/', '/friends')
api.add_resource(AddFriendResource, '/friends/add')