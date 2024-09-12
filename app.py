import sqlite3
from waitress import serve
from flask import Flask, render_template, redirect, send_file, jsonify, request, session
from flask_session import Session
from helpers import login_required, countries, topics

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


debateTopics = topics
debateLocalities = countries


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    
    session.clear()
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username or not password:
            return render_template("login.html", error="You have to enter both your username and your password to log in.")

        with sqlite3.connect("static/debate.db") as con:
            cur = con.cursor()
            cur.execute("SELECT id, hash FROM users WHERE username=?", [(username)])
            try:
                data = cur.fetchall()[0]
            except IndexError:
                return render_template("login.html", error="Username does not exist.")
            if password != data[1]:
                return render_template("login.html", error="Wrong password.")
            
            session["user_id"] = data[0]
            session["username"] = username
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        country = request.form.get("country")
        
        if not username or not password or not confirmation:
            return render_template("register.html", error="You must complete all fields to register.")
        if password != confirmation:
            return render_template("register.html", error="Password and confirmation are not the same.")
        if country == "Country":
            country = "NULL"
        
        with sqlite3.connect("static/debate.db") as con:
            cur = con.cursor()
            try:
                cur.execute("INSERT INTO users (username, hash, locality) VALUES(?,?,?)", [username, password, country])
            except sqlite3.IntegrityError:
                return render_template("register.html", countries=countries, error="Username already exists.")
        
        return redirect("/login")
    else:
        return render_template("register.html", countries=countries)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")


@app.route("/search")
@login_required
def search():
    return render_template("search.html")


@app.route("/query")
@login_required
def query():
    query = request.args.get("q")
    if query:
        with sqlite3.connect("static/debate.db") as con:
            cur = con.cursor()
            cur.execute("SELECT debateText FROM debates WHERE debateText LIKE ?", ['%' + query + '%'])
            results = cur.fetchall()
    else:
        results = []
    return jsonify(results)


@app.route("/create",  methods=["GET", "POST"])
@login_required
def create():
    if request.method == 'POST':
        debateText = request.form.get("debateText")
        debateTopic = request.form.get("debateTopic")
        debateLocality = request.form.get("debateLocality")
        
        if not debateText:
            return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities, error="You must write a debate teaser.")
        elif debateTopic not in debateTopics:
            return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities, error="You must select a valid topic for your debate.")
        elif debateLocality not in debateLocalities:
            return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities, error="You must precise a geographic scale for your debate.")
        
        with sqlite3.connect("static/debate.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO debates (user_id, debateText, debateTopic, locality) VALUES(?,?,?,?)", [session['user_id'], debateText, debateTopic, debateLocality])
        
        return redirect("/profile")
    else:
        return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities)


@app.route("/my-debates")
@login_required
def myDebates():
    return render_template("myDebates.html")


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", username=session["username"])


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/manifest.json")  #admin required?
def serve_manifest():
    return send_file("manifest.json", mimetype="application/manifest+json")


@app.route("/sw.js")  #admin required?
def serve_sw():
    return send_file("sw.js", mimetype="application/javascript")


if __name__ == '__main__':
    serve(app, port=8080)