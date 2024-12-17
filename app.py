import mysql.connector
from flask import Flask, render_template, redirect, send_file, jsonify, request, session
from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room, send
from helpers import login_required, get_data, hash_password, verify_password, countries, topics, bug_categories

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

async_mode = None
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")


debateTopics = topics
debateLocalities = countries
bug_categories = bug_categories


mydb = mysql.connector.connect(
  host="julianxbloom.mysql.pythonanywhere-services.com",
  user="julianxbloom",
  password="my_password",
  database="julianxbloom$debate"
)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    cur = mydb.cursor()

    cur.execute("SELECT debate_id FROM participants WHERE user_id=%s", (session.get("user_id"),))
    data = cur.fetchall()
    participating = tuple([i[0] for i in data])

    try:
        if len(participating) > 1:
            query = "SELECT id, user_id, debateText, debateTopic, locality FROM debates WHERE user_id<>%s AND id NOT IN {} LIMIT 2".format(participating)
            cur.execute(query, (session.get("user_id"),))
        elif len(participating) == 1:
            query = "SELECT id, user_id, debateText, debateTopic, locality FROM debates WHERE user_id<>%s AND id<>%s LIMIT 2"
            cur.execute(query, (session.get("user_id"), participating[0]))
        else:
            query = "SELECT id, user_id, debateText, debateTopic, locality FROM debates WHERE user_id<>%s LIMIT 2"
            cur.execute(query, (session.get("user_id"),))
        data = cur.fetchall()
    except:
        return render_template("index.html", debates=[])

    debates = []
    n = len(data)
    for i in range(n):
        cur.execute("SELECT username FROM users WHERE id=%s", (data[i][1],))
        username = cur.fetchall()[0][0]

        cur.execute("SELECT COUNT(id) FROM participants WHERE debate_id=%s", (data[i][0],))
        participants = cur.fetchall()[0][0]

        debates.append({"id": data[i][0], "text": data[i][2], "topic": data[i][3], "creator": username, "locality": data[i][4], "participants": participants})

    cur.close()

    return render_template("index.html", debates=debates)


@app.route("/data-update") #TO UPDATE
@login_required
def data_update():
    past_debates = eval(request.args.get("debates"))
    new_debates = get_data(past_debates=past_debates, mydb=mydb)
    return render_template("index.html", debates=new_debates)


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", error="You have to enter both your username and your password to log in.")

        cur = mydb.cursor()

        cur.execute("SELECT id, hash FROM users WHERE username=%s", (username,))
        try:
            data = cur.fetchall()[0]
        except IndexError:
            return render_template("login.html", error="Username does not exist.")
        if not verify_password(hash=data[1], password=password):
            return render_template("login.html", error="Wrong password.")

        cur.close()

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
            return render_template("register.html", countries=countries, error="You must complete all fields to register.")
        if len(password) > 20:
            return render_template("register.html", countries=countries, error="Password must not exceed 20 characters.")
        if len(username) > 15:
            return render_template("register.html", countries=countries, error="Username must not exceed 15 characters.")
        if password != confirmation:
            return render_template("register.html", countries=countries, error="Password and confirmation are not the same.")
        if country == "Country":
            country = "NULL"

        hashed_password = hash_password(password=password)


        cur = mydb.cursor()

        try:
            cur.execute("INSERT INTO users (username, hash, locality) VALUES(%s,%s,%s)", (username, hashed_password, country))
        except:
            return render_template("register.html", countries=countries, error="Username already exists.")

        mydb.commit()
        cur.close()

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
    cur = mydb.cursor()
    cur.execute("SELECT debate_id, COUNT(*) FROM participants GROUP BY debate_id ORDER BY COUNT(*) DESC LIMIT 8")
    data = cur.fetchall()

    popular_debates = []
    n = len(data)
    for i in range(n):

        cur.execute("SELECT debateText, debateTopic, locality FROM debates WHERE id=%s", (data[i][0],))
        debate_infos = cur.fetchall()
        print(debate_infos)

        popular_debates.append({'debate_id': data[i][0],'participants': data[i][1], 'debateText': debate_infos[0][0], 'debateTopic': debate_infos[0][1], 'locality': debate_infos[0][2]})

    cur.close()

    return render_template("search.html", popular_debates=popular_debates)


@app.route("/query")  #search query
@login_required
def query():
    query = request.args.get("q")
    if query:
        cur = mydb.cursor()
        cur.execute("SELECT id, debateText, debateTopic, locality FROM debates WHERE debateText LIKE %s", ('%' + query + '%',))
        results = cur.fetchall()
        cur.close()
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
            return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities, error="You must write a debate teaser.", teaser="")
        elif len(debateText) > 65:
            return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities, error="Debate teaser must not exceed 65 characters.", teaser=debateText)
        elif debateTopic not in debateTopics:
            return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities, error="You must select a valid topic for your debate.", teaser=debateText)
        elif debateLocality not in debateLocalities:
            return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities, error="You must precise a geographic scale for your debate.", teaser=debateText)

        cur = mydb.cursor()
        cur.execute("INSERT INTO debates (user_id, debateText, debateTopic, locality) VALUES(%s,%s,%s,%s)", (session.get('user_id'), debateText, debateTopic, debateLocality))
        mydb.commit()
        cur.close()

        return redirect("/profile")
    else:
        return render_template("create.html", debateTopics=debateTopics, debateLocalities=debateLocalities, teaser="")


@app.route("/active-debates")
@login_required
def myDebates():
    cur = mydb.cursor()
    cur.execute("SELECT debate_id FROM participants WHERE user_id=%s", (session.get("user_id"),))
    data = cur.fetchall()

    debates = []
    n = len(data)
    for i in range(n):
        debate_id = data[i][0]
        cur.execute("SELECT debateText, debateTopic, locality FROM debates WHERE id=%s", (debate_id,))
        tmp = cur.fetchall()
        debates.append({"id": debate_id, "text": tmp[0][0], "topic": tmp[0][1], "locality": tmp[0][2]})

    cur.close()

    return render_template("active-debates.html", debates=debates)


@app.route("/chat")
@login_required
def chat():
    query = request.args.get("q")
    if not query:
        return redirect("/")

    cur = mydb.cursor()

    cur.execute("SELECT debateText,user_id FROM debates WHERE id = %s", (query,))
    try:
        data = cur.fetchall()[0]
        text = data[0]
    except IndexError:
        return redirect("/")

    session['room_id'] = query


    cur.execute("SELECT username FROM users WHERE id=%s", (data[1],))
    creator = cur.fetchall()[0][0]

    cur.execute("SELECT * FROM participants WHERE debate_id=%s AND user_id=%s", (query, session["user_id"]))
    data = cur.fetchall()
    if data == []:
        cur.execute("INSERT INTO participants (debate_id, user_id) VALUES(%s,%s)", (query, session["user_id"]))
        mydb.commit()

    cur.execute("SELECT user_id, message, time FROM chats WHERE debate_id = %s", (query,))
    chat_data = cur.fetchall()

    sender_ids = tuple([chat[0] for chat in chat_data])
    senders = []
    n = len(sender_ids)
    for i in range(n):
        if sender_ids[i] == 0:
            sender = "deleted user"
        else:
            cur.execute("SELECT username FROM users WHERE id=%s",(sender_ids[i],))
            sender = cur.fetchall()[0][0]
        senders.append(sender)

    chats = []
    for i in range(n):
        chats.append({'sender_id': chat_data[i][0], 'sender': senders[i], 'message': chat_data[i][1]}) #maybe add time too?

    cur.close()

    return render_template("chat.html",chats=chats, room_id=query, debate_creator=creator, debate_text=text, username =session.get("username"))


@app.route("/profile")
@login_required
def profile():
    username = request.args.get("username")
    if not username:
        username = session.get("username")
    if username == "deleted user":
        return render_template("deleted-profile.html")

    cur = mydb.cursor()

    cur.execute("SELECT id, trust_score FROM users WHERE username=%s", (username,))
    data = cur.fetchall()
    user_id = data[0][0]
    trust_score = data[0][1]

    cur.execute("SELECT id, debateText, debateTopic, locality FROM debates WHERE user_id=%s", (user_id,))
    data = cur.fetchall()

    debates = []
    n = len(data)
    for i in range(n):
        debates.append({"id": data[i][0], "text": data[i][1], "topic": data[i][2], "locality": data[i][3]})

    cur.close()

    return render_template("profile.html", debates=debates, debate_length = len(debates) ,username=username, trust_score=trust_score, session_username=session.get("username"))


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/bug-feedback", methods=['GET', 'POST'])
@login_required
def bug_feedback():
    if request.method == 'POST':
        bug_category = request.form.get("bug-category")
        bug_description = request.form.get("bug-description")

        if not bug_description:
            return render_template("bug-feedback.html", bug_categories=bug_categories, bug_description="", error="You must describe the bug you want to give us feedback about!")
        elif len(bug_description) > 2000:
            return render_template("bug-feedback.html", bug_categories=bug_categories, bug_description=bug_description, error="Your bug report seems to be a bit too long..")
        elif  bug_category not in bug_categories:
            return render_template("bug-feedback.html", bug_categories=bug_categories, bug_description=bug_description, error="You must select a valid bug category.")

        cur = mydb.cursor()
        cur.execute("INSERT INTO bugs (category, description, bug_finder_id) VALUES (%s,%s,%s)", (bug_category, bug_description, session.get("user_id")))
        mydb.commit()

        cur.close()

        return redirect("/profile")

    return render_template("bug-feedback.html", bug_categories=bug_categories, bug_description="")


@app.route("/trust-score")
@login_required
def trust_score():
    return render_template("trust_score.html")


@app.route("/report", methods=['GET', 'POST'])
@login_required
def report():
    user_to_report = request.args.get("username")
    if not user_to_report:
        return redirect("/profile")
    if request.method == 'POST':
        text = request.form.get("report-text")
        if not text:
            return render_template("report.html", user_to_report=request.args.get("username"), error="You must describe the reason of your request.")
        if len(text) > 300:
            return render_template("report.html", user_to_report=request.args.get("username"), error="Report request must not exceed 300 characters.")

        reporting_user_id = session.get("user_id")

        cur = mydb.cursor()

        cur.execute("SELECT id FROM users WHERE username=%s", (user_to_report,))
        reported_user_id = cur.fetchall()[0][0]

        cur.execute("INSERT INTO reports (reported_user_id, reporting_user_id, text) VALUES (%s,%s,%s)", (reported_user_id, reporting_user_id, text))
        mydb.commit()

        cur.close()

        return redirect("/profile?username={}".format(user_to_report))
    return render_template("report.html", user_to_report=request.args.get("username"))


@app.route("/delete") #deleting debate
@login_required
def delete():
    to_delete = request.args.get("debate_id")
    if not to_delete:
        return redirect("/")

    cur = mydb.cursor()

    cur.execute("SELECT user_id FROM debates WHERE id=%s", (to_delete,))
    debate_creator = cur.fetchall()[0][0]

    if debate_creator == session["user_id"]:
        cur.execute("DELETE FROM chats WHERE debate_id=?", [to_delete])
        cur.execute("DELETE FROM participants WHERE debate_id=?", [to_delete])
        cur.execute("DELETE FROM debates WHERE id=?", [to_delete])
        mydb.commit()
        cur.close()
        return redirect("/profile")

    else:
        cur.execute("DELETE FROM participants WHERE debate_id=%s AND user_id=%s", (to_delete, session.get('user_id')))
        mydb.commit()
        cur.close()
        return redirect("/active-debates")


@app.route("/del-account", methods=["GET", "POST"])
@login_required
def del_account():
    if request.method == 'POST':
        cur = mydb.cursor()

        user_id = session.get('user_id')

        cur.execute("UPDATE chats SET user_id=? WHERE user_id=%s", (0, user_id))
        cur.execute("DELETE FROM participants WHERE user_id=%s", (user_id,))
        cur.execute("DELETE FROM debates WHERE user_id=%s", (user_id,))
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))

        mydb.commit()
        cur.close()

        return redirect("/logout")

    else:
        return render_template("del-confirm.html")




@app.route("/manifest.json")  #admin required?
def serve_manifest():
    return send_file("manifest.json", mimetype="application/manifest+json")


@app.route("/sw.js")  #admin required?
def serve_sw():
    return send_file("sw.js", mimetype="application/javascript")




@socketio.on('connect')
def handle_connect():
    room_id = session.get('room_id')
    username = session.get('username')

    if not username or not room_id:
        return
    else:
        join_room(room_id)


@socketio.on('message')
def handle_message(data):
    room_id = session.get('room_id')

    message = {
        'sender': session.get("username"),
        'message':data['message']
    }

    cur = mydb.cursor()
    cur.execute("INSERT INTO chats (debate_id, user_id, message) VALUES(%s,%s,%s)", (room_id, session.get("user_id"), message['message']))
    mydb.commit()
    cur.close()

    send(message, to=room_id)


@socketio.on('disconnect')
def handle_disconnect():
    room_id = session.get('room_id')
    leave_room(room_id)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080)
