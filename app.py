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
    with sqlite3.connect("static/debate.db") as con:
        cur = con.cursor()
        cur.execute("SELECT id, user_id, debateText, debateTopic, locality FROM debates LIMIT 10") #TO IMPROVE
        data = cur.fetchall()
        
        debates = []
        n = len(data)
        for i in range(n):
            cur.execute("SELECT username FROM users WHERE id=?", [data[i][1]])
            username = cur.fetchall()[0][0]
            
            debates.append({"id": data[i][0], "text": data[i][2], "topic": data[i][3], "creator": username, "locality": data[i][4]})
    return render_template("index.html", debates=debates)


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


@app.route("/query")  #search query
@login_required
def query():
    query = request.args.get("q")
    if query:
        with sqlite3.connect("static/debate.db") as con:
            cur = con.cursor()
            cur.execute("SELECT id, debateText, debateTopic, locality FROM debates WHERE debateText LIKE ?", ['%' + query + '%'])
            results = cur.fetchall()
    else:
        results = []
    return jsonify(results)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == 'POST':
        debateText = request.form.get("debateText")
        debateTopic = request.form.get("debateTopic")
        debateLocality = request.form.get("debateLocality")
        
        if not debateText:
            return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities, error="You must write a debate teaser.")
        elif len(debateText) > 70:
            return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities, error="Debate teaser must not exceed 70 characters.", teaser=debateText)
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


@app.route("/active-debates")
@login_required
def myDebates():
    with sqlite3.connect("static/debate.db") as con:
        cur = con.cursor()
        cur.execute("SELECT debate_id FROM participants WHERE user_id=?", [session["user_id"]])
        data = cur.fetchall()
        
        debates = []
        n = len(data)
        for i in range(n):
            debate_id = data[i][0]
            cur.execute("SELECT debateText, debateTopic, locality FROM debates WHERE id=?", [debate_id])
            tmp = cur.fetchall()
            debates.append({"id": debate_id, "text": tmp[0][0], "topic": tmp[0][1], "locality": tmp[0][2]})

    return render_template("active-debates.html", debates=debates)


@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    query = request.args.get("q")
    
    if request.method == 'POST':
        message = request.form.get("message")
        with sqlite3.connect("static/debate.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO chats (debate_id, user_id, message) VALUES(?,?,?)", [query, session["user_id"], message])
        
        return redirect("/chat?q={query}".format(query=query))
    
    else:
        if not query:
            return redirect("/")
        
        with sqlite3.connect("static/debate.db") as con:
            cur = con.cursor()

            cur.execute("SELECT debateText FROM debates WHERE id = ?", [query])
            try: 
                text = cur.fetchall()[0][0]
            except IndexError:
                return redirect("/")
            
            cur.execute("SELECT * FROM participants WHERE debate_id = ? AND user_id = ?", [query, session["user_id"]])
            data = cur.fetchall()
            if data == []:
                cur.execute("INSERT INTO participants (debate_id, user_id) VALUES(?,?)", [query, session["user_id"]])
            
            cur.execute("SELECT user_id, message, time FROM chats WHERE debate_id = ?", [query])
            chats = cur.fetchall()
        
        return render_template("chat.html", debate_id=query, chats=chats, debate_text=text, session_id=session["user_id"])


@app.route("/profile")
@login_required
def profile():
    with sqlite3.connect("static/debate.db") as con:
        cur = con.cursor()
        cur.execute("SELECT id, debateText, debateTopic, locality FROM debates WHERE user_id=?", [session["user_id"]])
        data = cur.fetchall()

        debates = []
        n = len(data)
        for i in range(n):
            debates.append({"id": data[i][0], "text": data[i][1], "topic": data[i][2], "locality": data[i][3]})

    return render_template("profile.html", debates=debates, debate_length = len(debates) ,username=session["username"])


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