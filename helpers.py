import sqlite3
from flask import redirect, session
from functools import wraps
import argon2


    # Fuctions

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def get_data(past_debates=[]) -> list[dict]:
    past_ids = tuple([debate['id'] for debate in past_debates])
    
    with sqlite3.connect("static/debate.db") as con:
        cur = con.cursor()
        
        cur.execute("SELECT debate_id FROM participants WHERE user_id=?", [session["user_id"]])
        data = cur.fetchall()
        participating = tuple([ele[0] for ele in data])
        
        try:
            query = "SELECT id, user_id, debateText, debateTopic, locality FROM debates WHERE user_id<>? AND id NOT IN {} AND id NOT IN {} LIMIT 50".format(past_ids, participating)
            cur.execute(query, [session["user_id"]])
        except sqlite3.OperationalError:
            return []
        data = cur.fetchall()
        
        debates = []
        n = len(data)
        for i in range(n):
            cur.execute("SELECT username FROM users WHERE id=?", [data[i][1]])
            username = cur.fetchall()[0][0]

            cur.execute("SELECT COUNT(id) FROM participants WHERE debate_id=?", [data[i][0]])
            participants = cur.fetchall()[0][0]
            
            debates.append({"id": data[i][0], "text": data[i][2], "topic": data[i][3], "creator": username, "locality": data[i][4], "participants": participants})

    return debates


def hash_password(password: str):
    return argon2.PasswordHasher().hash(password)


def verify_password(hash: str | bytes, password: str) -> bool:
    try:
        verify = argon2.PasswordHasher().verify(hash=hash, password=password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False



    # Variables

bug_categories = ['Debate scrolling', 'Search', 'Debate creation', 'Chatting', 'Profile / trust score', 'Other']

topics = [
    "Politics", "Social", "Economics", "Education", "Health", "Technology", "Other"
    ]

countries = [
    "Afghanistan",
    "Albania",
    "Algeria",
    "Andorra",
    "Angola",
    "Argentina",
    "Armenia",
    "Aruba",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bermuda",
    "Bhutan",
    "Bolivia",
    "Bosnia and Herzegovina",
    "Botswana",
    "Brazil",
    "Brunei",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Colombia",
    "Congo Republic",
    "Costa Rica",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "DR Congo",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Ethiopia",
    "Fiji",
    "Finland",
    "France",
    "Gabon",
    "Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Gibraltar",
    "Greece",
    "Guatemala",
    "Guinea",
    "Guyana",
    "Haiti",
    "Honduras",
    "Hong Kong",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Ireland",
    "Italy",
    "Ivory Coast",
    "Jamaica",
    "Japan",
    "Kazakhstan",
    "Kenya",
    "Kosovo",
    "Kuwait",
    "Kyrgyzstan",
    "Laos",
    "Libya",
    "Lithuania",
    "Luxembourg",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Mali",
    "Malta",
    "Mexico",
    "Monaco",
    "Mongolia",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nauru",
    "Nepal",
    "Netherlands",
    "New Caledonia",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "North Korea",
    "Norway",
    "Oman",
    "Pakistan",
    "Palau",
    "Palestine",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Philippines",
    "Poland",
    "Portugal",
    "Puerto Rico",
    "Qatar",
    "Romania",
    "Russia",
    "Rwanda",
    "Samoa",
    "San Marino",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Somalia",
    "South Africa",
    "South Korea",
    "South Sudan",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Sweden",
    "Switzerland",
    "Syria",
    "Taiwan",
    "Tajikistan",
    "Thailand",
    "Togo",
    "Tonga",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States of America",
    "Uruguay",
    "Uzbekistan",
    "Venezuela",
    "Vietnam",
    "Western Sahara",
    "Yemen",
    "Zambia",
    "Zimbabwe",
    ]