from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('playlist_title')
parser.add_argument('song_title')
parser.add_argument('artist')
app = Flask("playlists")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="playlists", user="postgres", password="postgres", host="playlists_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def create_playlist(username, playlist_title):
    user_exists = True
    response = requests.get("http://authentication:5000/authentication/" +  username)
    if response.status_code == 200:
        user_exists = response.json()["data"]
    if user_exists:
        cur = conn.cursor()
        cur.execute("INSERT INTO playlists (username, title) VALUES (%s, %s);", (username, playlist_title))
        conn.commit()
        description = "Created a playlist named " + playlist_title
        response = requests.post("http://activities:5000/activities/" +  username + "?description=" + description)
        return True
    return False

def get_allPlaylists(username):
    user_playlists = []
    shared_playlists = []
    user_exists = True
    response = requests.get("http://authentication:5000/authentication/" +  username)
    if response.status_code == 200:
        user_exists = response.json()["data"]
    if user_exists:
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM playlists WHERE username = %s;", (username,))
        rows = cur.fetchall()
        for row in rows:
            id, title = row
            user_playlists.append((id, title))
        conn.rollback()
        cur.execute("SELECT id, title FROM playlists WHERE %s = ANY(shared_with);", (username, ))
        rows = cur.fetchall()
        for row in rows:
            id, title = row
            shared_playlists.append((id, title))
        return {"my_playlists": user_playlists, "shared_with_me": shared_playlists}
    return {"my_playlists": [], "shared_with_me": []}
def invite(playlist_id, recipient, username):
    user_exists = True
    response = requests.get("http://authentication:5000/authentication/" +  username)
    if response.status_code == 200:
        user_exists = response.json()["data"]
    cur = conn.cursor()
    cur.execute("SELECT shared_with FROM playlists WHERE id = %s;", (playlist_id,))
    result = cur.fetchone()
    shared_with = result[0]
    recipient_exists = True
    response = requests.get("http://authentication:5000/authentication/" +  recipient)
    if response.status_code == 200:
        recipient_exists = response.json()["data"]
    if user_exists and recipient_exists and recipient != username and recipient not in shared_with:
        conn.rollback()
        cur.execute(
        "UPDATE playlists "
        "SET shared_with = array_append(shared_with, %s) "
        "WHERE id = %s;",
        (recipient, playlist_id)
        )
        conn.commit()
        description = "Shares playlist with " + recipient
        response = requests.post("http://activities:5000/activities/" +  username + "?description=" + description)
        return True
    return False
def addSong(playlist_id, title, artist, username):
    user_exists = True
    response = requests.get("http://authentication:5000/authentication/" +  username)
    if response.status_code == 200:
        user_exists = response.json()["data"]
    response = requests.get("http://songs:5000/songs/exist/?title=" + title + "&artist=" + artist)
    song_exists = True
    if response.status_code == 200:
        song_exists = response.json()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM songs WHERE title = %s AND artist = %s AND playlist_id = %s;", (title, artist, playlist_id))
    count = cur.fetchone()[0]
    conn.rollback()
    if song_exists and user_exists and count == 0:
        cur.execute("INSERT INTO songs (title, artist, playlist_id) VALUES (%s, %s, %s);", (title, artist, playlist_id))
        conn.commit()
        description = "Added a song to a playlist"
        response = requests.post("http://activities:5000/activities/" +  username + "?description=" + description)
        return True
    return False

def getSongs(playlist_id):
    cur = conn.cursor()
    cur.execute("SELECT title, artist FROM songs WHERE playlist_id = %s;", (playlist_id, ))
    return cur.fetchall()

class PlaylistResource(Resource):
    def post(self, username=None):
        try:
            args = flask_request.args
            result = create_playlist(username, args['playlist_title'])
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
        
    def get(self, username=None):
        try:
            result = get_allPlaylists(username)
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500

class SharePlaylistResource(Resource):
    def put(self, playlist_id, recipient, username):
        try:
            result = invite(playlist_id, recipient, username)
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
class AddSongResource(Resource):
    def post(self, playlist_id, username):
        try:
            args = flask_request.args
            result =  addSong(playlist_id, args['song_title'], args['artist'], username)
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
class SongResource(Resource):
    def get(self, playlist_id):
        try:
            result =  getSongs(playlist_id)
            return {"data": result}, 200
        except Exception as e:
            error_message = str(e)
            return {"data": error_message}, 500
api.add_resource(PlaylistResource, '/playlists/<string:username>', '/playlists/', '/playlists')
api.add_resource(SharePlaylistResource, '/playlists/<string:username>/<string:playlist_id>/share/<string:recipient>')
api.add_resource(AddSongResource, '/playlists/<string:username>/<string:playlist_id>')
api.add_resource(SongResource, '/playlists/<string:playlist_id>/songs')
