import mysql.connector
from texttable import Texttable
from helpers import verify_password

password = str(input("Password: "))
hash_file = open("admin_password.txt", 'r')
hash = hash_file.read()
while not verify_password(password=password, hash=hash):
    print("Wrong password.")
    password = str(input("Password: "))


def process(q):
    begin = q[0]
    if begin == "help":
        help()
    elif begin == "display":
        display(q)
    elif begin == "validate":
        validate(q)
    elif begin == "delete":
        delete(q)
    elif begin == "ban":
        ban(q)
    elif begin == "history":
        history(q)
    else:
        print("unknown command")

def help():
    print("leave: to leave this terminal")
    print("display [command]: displays either reports, bans or bugs")
    print("validate [report id]: validates a report")
    print("delete [item] [id]: deletes item (report, ban or bug) that has the given id")
    print("ban [username]: bans a given user from Debate")
    print("history [username]: displays the chat history of a given user")


def display(q):
    try:
        command = q[1]
    except IndexError:
        print("you have to precise a command to tell what you want to display")
        return

    if command == "reports":
        with mysql.connector.connect(
            host="julianxbloom.mysql.pythonanywhere-services.com",
            user="julianxbloom",
            password="my_password",
            database="julianxbloom$debate",
        ) as mydb:

            cur = mydb.cursor()

            cur.execute("SELECT reports.id, users.username, reports.text FROM reports JOIN users ON users.id = reports.reported_user_id")
            data = cur.fetchall()

            table = Texttable()
            table.add_row(['N°', 'Reported User', 'Reason'])
            for ele in data:
                table.add_row([ele[0], ele[1], ele[2]])
            print(table.draw())

            cur.close()

    elif command == "bans":
        with mysql.connector.connect(
            host="julianxbloom.mysql.pythonanywhere-services.com",
            user="julianxbloom",
            password="my_password",
            database="julianxbloom$debate",
        ) as mydb:

            cur = mydb.cursor()

            cur.execute("SELECT * FROM bans")
            data = cur.fetchall()

            table = Texttable()
            table.add_row(['N°', 'User', 'Started on', 'Banned for (days)'])
            for ele in data:
                table.add_row([ele[0], ele[1], ele[2], ele[3]])
            print(table.draw())

            cur.close()

    elif command == "bugs":
        with mysql.connector.connect(
            host="julianxbloom.mysql.pythonanywhere-services.com",
            user="julianxbloom",
            password="my_password",
            database="julianxbloom$debate",
        ) as mydb:

            cur = mydb.cursor()

            cur.execute("SELECT * FROM bugs")
            data = cur.fetchall()

            table = Texttable()
            table.add_row(['N°', 'Category', 'Description'])
            for ele in data:
                table.add_row([ele[0], ele[1], ele[2]])
            print(table.draw())

            cur.close()

    else:
        print("unknow command")


def validate(q):
    try:
        report_id = int(q[1])
    except IndexError:
        print("you have to precise a report id")
        print("\n")
        return


    with mysql.connector.connect(
            host="julianxbloom.mysql.pythonanywhere-services.com",
            user="julianxbloom",
            password="my_password",
            database="julianxbloom$debate",
        ) as mydb:

        cur = mydb.cursor()

        cur.execute("SELECT id FROM reports")
        data = cur.fetchall()
        report_ids = [ele[0] for ele in data]
        if report_id not in report_ids:
            print("wrong report id")
            print("\n")
            return

        print("How many Trust Score should the user loose? (default: 5)")
        dminus = int(input())

        print("You are about to validate a report that will make loose the user {} Trust Score points. Do you agree?".format(dminus))
        validation = str(input("type 'y'/'n': "))
        while validation not in ('y', 'n'):
            validation = str(input("type 'y'/'n': "))
        if validation == 'n':
            print("report validation canceled")
            print("\n")
            return
        else:
            cur.execute("SELECT users.id, users.trust_score FROM users JOIN reports ON reports.reported_user_id = users.id WHERE reports.id = %s",
                        (report_id,))
            data = cur.fetchall()
            user_id, trust_score = data[0][0], data[0][1]
            print(user_id, trust_score)

            new_trust_score = trust_score - dminus
            print(new_trust_score)

            if new_trust_score < 20:
                cur.execute("INSERT INTO bans (user_id) VALUES (%s)", (user_id,))

            cur.execute("UPDATE users SET trust_score=%s WHERE id=%s", (new_trust_score, user_id))

            print(report_id)
            cur.execute("DELETE FROM reports WHERE id=%s", (report_id,))

        mydb.commit()
        cur.close()
        print("report validated")
        print("\n")


def delete(q):
    try:
        item = q[1]
        id = int(q[2])
    except IndexError:
        print("written wrong, type 'help' to get details about how to use this command")
        print("\n")
        return

    with mysql.connector.connect(
            host="julianxbloom.mysql.pythonanywhere-services.com",
            user="julianxbloom",
            password="my_password",
            database="julianxbloom$debate",
        ) as mydb:

        cur = mydb.cursor()

        if item == "report":
            cur.execute("DELETE FROM reports WHERE id=%s", (id,))
        elif item == "ban":
            cur.execute("DELETE FROM bans WHERE id=%s", (id,))
        elif item == "bug":
            cur.execute("DELETE FROM bugs WHERE id=%s", (id,))
        else:
            print("wrong item type")
            print("\n")
            return

        mydb.commit()
        cur.close()
        print("item successfully deleted (also displays this message if the id typed does not exist)")
        print("\n")


def ban(q):
    try:
        username = q[1]
    except IndexError:
        print("you have to precise a username")
        print("\n")
        return

    with mysql.connector.connect(
            host="julianxbloom.mysql.pythonanywhere-services.com",
            user="julianxbloom",
            password="my_password",
            database="julianxbloom$debate",
        ) as mydb:

        cur = mydb.cursor()

        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        try:
            user_id = cur.fetchall()[0][0]
        except IndexError:
            print("wrong username")
            print("\n")
            return

        cur.execute("UPDATE users SET trust_score=%s WHERE username=%s", (10, username))
        cur.execute("INSERT INTO bans (user_id) VALUES (%s)", (user_id,))

        mydb.commit()
        cur.close()
        print("user successfully banned")
        print("\n")


def history(q):
    try:
        username = q[1]
    except IndexError:
        print("you have to precise a username")
        print("\n")
        return

    with mysql.connector.connect(
            host="julianxbloom.mysql.pythonanywhere-services.com",
            user="julianxbloom",
            password="my_password",
            database="julianxbloom$debate",
        ) as mydb:

        cur = mydb.cursor()

        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        try:
            user_id = cur.fetchall()[0][0]
        except IndexError:
            print("wrong username")
            print("\n")
            return

        cur.execute("SELECT message, time FROM chats WHERE user_id=%s", (user_id,))
        data = cur.fetchall()

        table = Texttable()
        table.add_row(['Time', 'Message'])
        for ele in data:
            table.add_row([ele[1], ele[0]])
        print(table.draw())

        mydb.commit()
        cur.close()
        print("\n")



print("Successfully connected as a Debate admin. Type 'help' to know more about this interface.")
print("\n")
query = ""
running = True
while running:
    print("$", end="")
    query = str(input()).split()

    if query[0] == "leave":
        running = False
        continue

    process(query)

