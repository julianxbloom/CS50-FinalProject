# DEBATE.
### Video Presentation: TO ADD

<b>Debate.</b> is a social network that allow you to debate about any subject you want with anybody. You can set your own debate and wait for others to join it.
<br>
It is designed for Android devices only.

The app is programmed using Python's [Flask](https://flask.palletsprojects.com/en/) library for the server side, and HTML/CSS/Javascript for the client side. It is worth noticing the use of [Bootstrap](https://getbootstrap.com/) in add to the css code.
The webapp is hosted on Pythonanywhere at the following URL: https://julianxbloom.pythonanywhere.com. Its database is stored using MySQL.

Users have the ability to:
  - create new debates
  - live-chat with other users about a specific debate (programmed using [flask-socketio](https://flask-socketio.readthedocs.io/en/latest/), and adapted to Pythonanywhere using [this](https://help.pythonanywhere.com/pages/FlaskSocketIO/) help page)
  - join any debate they want (by scrolling in the main menu or searching for a debate)

Moreover, this app is designed as a Progressive Web Application (also know as PWA). This means it can be downloaded from your web browser directly to your phone. It will then appear as any other application. For more information about PWA's, look at [this link](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
