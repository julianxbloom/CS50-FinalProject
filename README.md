# DEBATE.
### Video Presentation: TO ADD

**Debate.** is a social network that allows you to debate about any subject you want with anybody. You can set your own debate and wait for others to join it. Then, you can communicate with them throught a chat, ruled by **Trust Score**, a score that reflects debaters' behaviour.

# Libraries and external tools used

The app is programmed using Python's [Flask](https://flask.palletsprojects.com/en/) library for the server side, and HTML, CSS and Javascript for the client side. To that extent, the project has to fit with Flask's required file architecture: a app.py file ([accessible here](https://github.com/julianxbloom/CS50-FinalProject/blob/main/app.py)), containing the several routes users can go througth when using the app, a static folder, containing all icons displayed in the app and a templates folder, where the html templates for each route are stored. In add to these files, I separated from functions and variables from app.py, and put them in helpers.py (have a look at the code clicking [here](https://github.com/julianxbloom/CS50-FinalProject/blob/main/helpers.py)). It helps lighten the main file of the webapp, insomuch as the list containing localities is really long. 
Likewise, it is worth noticing the use of [Bootstrap](https://getbootstrap.com/) in add to self-written css stylesheets.
<br><br>
The webapp is hosted on [Pythonanywhere](https://www.pythonanywhere.com/) at the following URL: https://www.julianxbloom.pythonanywhere.com/. It is an online web hosting service. This web host was not my first choice, as I began an implementation on Microsoft Azure (Microsoft's cloud services). But the complexity of Azure, being used for a lot of different activities, made it very hard to manage a "simple" web application. On the contrary, Pythonanywhere has a more user-friendly interface and focuses only on webapplications, which made it easier for me to implement my app on this host.
<br><br>
Data about the users is stored in a database, as well as data about every specific debate and even more. This database is stored on Pythonanywhere too, and managed by MySQL, a database management system that is quite similar to sqlite. 
<br>
Here is the relational diagram of **Debate.**'s database:

![database diagram](database_diagram.png)

It is worth mentionning passwords are hashed using [Argon2 for Python](https://argon2-cffi.readthedocs.io/en/stable/), a module which mainly offers a hashing function and another to compare a given password to the hash produced previously. I tried to make the hashing function myself, but I quickly realized the importance of security issues, and my lack of knowledge in cryptography and cybersecurity in general pushed me to select an existant hashing algorithm I can trust.

At last, if you take a look at requirements.txt, you will realize I used specific versions of several libraries. In fact, combining such an amount of different python libraries between them and with the web host required an important work of library version coordination. As an example, some libraries don't interact well with others since a version X of the library, so it is necessary to use past versions of one of the two librabies (or both) to be able to make them interact one to another.

WATCH OUT! It is important to mention the app is designed for **Android devices** only.


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
To me, it is really important to get feedback from the users of my webapp. To this extent, I added the possibility for the users to provide a feedback, througth the "Bug Feedback" page, found in the app's settings. More than being only a way to discover new bugs, it can also be a way to communicate with the users and find ways to improve their experience on the app.

