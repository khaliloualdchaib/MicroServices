from flask import Flask, render_template, redirect, request, url_for
import requests

app = Flask(__name__)


# The Username & Password of the currently logged-in User
username = None
password = None

session_data = dict()


def save_to_session(key, value):
    session_data[key] = value


def load_from_session(key):
    return session_data.pop(key) if key in session_data else None  # Pop to ensure that it is only used once


@app.route("/")
def feed():
    # ================================
    # FEATURE 9 (feed)
    #
    # Get the feed of the last N activities of your friends.
    # ================================

    global username

    N = 10

    if username is not None:
        feed = []  # TODO: call
        response = requests.get("http://activities:5000/activities/" + username + "?count=" + str(N))
        if response.status_code == 200:
            feed = response.json()["data"]
    else:
        feed = []

    return render_template('feed.html', username=username, password=password, feed=feed)


@app.route("/catalogue")
def catalogue():
    songs = requests.get("http://songs:5000/songs").json()

    return render_template('catalogue.html', username=username, password=password, songs=songs)


@app.route("/login")
def login_page():

    success = load_from_session('success')
    return render_template('login.html', username=username, password=password, success=success)


@app.route("/login", methods=['POST'])
def actual_login():
    req_username, req_password = request.form['username'], request.form['password']
    # ================================
    # FEATURE 2 (login)
    #
    # send the username and password to the microservice
    # microservice returns True if correct combination, False if otherwise.
    # Also pay attention to the status code returned by the microservice.
    # ================================
    success = None  # TODO: call
    response = requests.post("http://authentication:5000/authentication/login?username=" + req_username + "&password=" + req_password)
    if response.status_code == 200:
        success = response.json()["data"]
    if success:
        global username, password
        username = req_username
        password = req_password

    return redirect('/login')


@app.route("/register")
def register_page():
    success = load_from_session('success')
    return render_template('register.html', username=username, password=password, success=success)


@app.route("/register", methods=['POST'])
def actual_register():

    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE 1 (register)
    #
    # send the username and password to the microservice
    # microservice returns True if registration is succesful, False if otherwise.
    #
    # Registration is successful if a user with the same username doesn't exist yet.
    # ================================

    success = None  # TODO: call

    response = requests.post("http://authentication:5000/authentication/register?username=" + req_username + "&password=" + req_password)
    if response.status_code == 200:
        succes = response.json()["data"]
    save_to_session('success', success)

    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect('/register')


@app.route("/friends")
def friends():
    success = load_from_session('success')

    global username

    # ================================
    # FEATURE 4
    #
    # Get a list of friends for the currently logged-in user
    # ================================
    if username is not None:
        response = requests.get("http://friends:5000/friends/" + username)
        if response.status_code == 200:
            friend_list = response.json()["data"]
        else:
            friend_list = []
    else:
        friend_list = []  # TODO: call

    return render_template('friends.html', username=username, password=password, success=success, friend_list=friend_list)


@app.route("/add_friend", methods=['POST'])
def add_friend():

    # ==============================
    # FEATURE 3
    #
    # send the username of the current user and the username of the added friend to the microservice
    # microservice returns True if the friend request is successful (the friend exists & is not already friends), False if otherwise
    # ==============================

    global username
    req_username = request.form['username']

    success = None  # TODO: call
    response = requests.post("http://friends:5000/friends/add?username=" + username + "&username_friend=" + req_username)
    if response.status_code == 200:
        success = response.json()["data"]
    save_to_session('success', success)    
    return redirect('/friends')


@app.route('/playlists')
def playlists():
    global username

    my_playlists = []
    shared_with_me = []

    if username is not None:
        # ================================
        # FEATURE
        #
        # Get all playlists you created and all playlist that are shared with you. (list of id, title pairs)
        # ================================

        my_playlists = []  # TODO: call
        shared_with_me = []  # TODO: call
        response = requests.get("http://playlists:5000/playlists/" + username)
        if response.status_code == 200:
            my_playlists = response.json()["data"]["my_playlists"]
            shared_with_me = response.json()["data"]["shared_with_me"]

    return render_template('playlists.html', username=username, password=password, my_playlists=my_playlists, shared_with_me=shared_with_me)


@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    # ================================
    # FEATURE 5
    #
    # Create a playlist by sending the owner and the title to the microservice.
    # ================================
    global username
    title = request.form['title']

    # TODO: call
    response = requests.post("http://playlists:5000/playlists/" + username + "?playlist_title=" + title)
    return redirect('/playlists')


@app.route('/playlists/<int:playlist_id>')
def a_playlist(playlist_id):
    # ================================
    # FEATURE 7
    #
    # List all songs within a playlist
    # ================================
    songs = [] # TODO: call
    response = requests.get("http://playlists:5000/playlists/" + str(playlist_id) + "/songs")
    songs = response.json()["data"]
    return render_template('a_playlist.html', username=username, password=password, songs=songs, playlist_id=playlist_id)


@app.route('/add_song_to/<int:playlist_id>', methods=["POST"])
def add_song_to_playlist(playlist_id):
    # ================================
    # FEATURE 6
    #
    # Add a song (represented by a title & artist) to a playlist (represented by an id)
    # ================================
    title, artist = request.form['title'], request.form['artist']
    response = requests.post("http://playlists:5000/playlists/" + username + "/" + str(playlist_id) + "?song_title=" + title + "&artist=" + artist)
    # TODO: call
    return redirect(f'/playlists/{playlist_id}')


@app.route('/invite_user_to/<int:playlist_id>', methods=["POST"])
def invite_user_to_playlist(playlist_id):
    # ================================
    # FEATURE 8
    #
    # Share a playlist (represented by an id) with a user.
    # ================================
    recipient = request.form['user']

    # TODO: call
    response = requests.put("http://playlists:5000/playlists/" + username + "/" + str(playlist_id) + "/share/" + recipient)
    return redirect(f'/playlists/{playlist_id}')


@app.route("/logout")
def logout():
    global username, password

    username = None
    password = None
    return redirect('/')
