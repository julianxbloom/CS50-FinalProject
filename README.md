# DEBATE.
### Video Presentation: TO ADD

**Debate.** is a social network that allows you to debate about any subject you want with anybody. You can set your own debate and wait for others to join it. Then, you can communicate with them throught a chat, ruled by **Trust Score**, a score that reflects debaters' behaviour.

# Libraries and external tools used

The app is programmed using Python's [Flask](https://flask.palletsprojects.com/en/) library for the server side, and HTML, CSS and Javascript for the client side. It is worth noticing the use of [Bootstrap](https://getbootstrap.com/) in add to self-written css stylesheets.
<br><br>
The webapp is hosted on [Pythonanywhere](https://www.pythonanywhere.com/) at the following URL: https://www.julianxbloom.pythonanywhere.com/. It is an online web hosting service, but it also contains a MySQL server on which I was able to host the app's database.
<br><br>
Data about the users is stored in this database, as well as data about every specific debate and even more. Here is the relational diagram of **Debate.**'s database:

![database diagram](database_diagram.png)

It is worth mentionning passwords are hashed using [Argon2 for Python](https://argon2-cffi.readthedocs.io/en/stable/), a module which mainly offers a hashing function and another to compare a given password to the hash produced previously. I tried to make the hashing function myself, but I quickly realized the importance of security issues, and my lack of knowledge in cryptography and cybersecurity in general pushed me to select an existant hashing algorithm I can trust.

Lastly, it is important to mention the app is designed for **Android devices** only.


# Features
## Fundamentals
Users have the ability to:
<ul>
  <li><b>create</b> new debates: they can decide of the debate's hook, its topic and eventually its locality.</li>
  <li><b>live-chat</b> with other users about a specific debate: programmed using <a href="https://flask-socketio.readthedocs.io/en/latest/">flask-socketio</a>, and adapted to Pythonanywhere using <a href="https://help.pythonanywhere.com/pages/FlaskSocketIO/">this</a> help page, live-chatting allows users to connect with each other.</li>
  <li><b>join</b> any debate they want: in the main menu, users can scroll throught the others' debates. Moreover, they can search for a specific debate or topic using the searching interface. The latter also displays most popular debates. </li>
</ul>

## Moderation
The conversations are ruled around **Trust Score**: a rate out of a hundread that is meant to reflect the user's good or bad behaviour on the app. This score is accessible throught any user's profile page, as well as details about the sanctions that can be encoutered: in brief, low Trust Score will lead to a temporary ban from Debate.
<br><br>
The debaters are able to report the others throught their profile page, a report that will be count as valid after having being read by an administrator of the app. Indeed, adminstrators can use the programmed administration console to manage users. It gives them the ability to proceed bugs and reports, to access users' chat history and to ban users. Look at [admin.py](https://github.com/julianxbloom/CS50-FinalProject/blob/main/admin.py) file for more information about the console's features.

# PWA
Moreover, this app is designed as a **Progressive Web Application** (also know as PWA). This means it can be downloaded from your web browser directly to your phone. It will then appear as any other application. To do this, as with Flask's specific architecture, PWAs need two specific files: a json manifest ([here](https://github.com/julianxbloom/CS50-FinalProject/blob/main/manifest.json)) and a service worker coded in javascript ([here](https://github.com/julianxbloom/CS50-FinalProject/blob/main/sw.js)).

The manifest contains data about the app itself such as its name, paths to the icons that will be displayed on the phone menu and the scope of the PWA: the "default" place we should be sent to when launching the app. While on its side, the service worker's job is to ensure the app will be launchable even if the user is not connected to Internet, or if the web server is currently not working. It does so by storing part of the webapp in a dedicated cache.

For more information about PWAs, look at [this link](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps).


# Bug feedback

In the app's settings, users are able to provide a feedback to the developers, a good help to spot unexpected bugs...

