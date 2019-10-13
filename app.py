from flask import Flask, render_template, session, request, redirect
from flask_session import Session
from tempfile import mkdtemp
from config import Config
import requests
import json
import smtplib
import ssl


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/check', methods=["GET", "POST"])
def call_weather():
    zip_code = request.form["zip_code"]
    api_key = Config.weather_api

    # call function to get coordinates from zip code
    coordinates = zip_to_coord(zip_code)

    url = f'https://api.darksky.net/forecast/{api_key}/{coordinates[0]},{coordinates[1]}'
    request_response = requests.get(url)

    response_json = json.loads(request_response.text)
    return render_template("forecast.html", zip_code=zip_code, forecast=response_json)


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/email', methods=["POST"])
def email():
    email = request.form['email']
    comments = request.form['comments']
    port = 465  # For SSL
    password = Config.email_password
    sender_email = Config.sender_email
    receiver_email = sender_email
    message = f"""\
        From: {email}
        
        Subject: Feedback from {email}

        {comments}"""

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    
    return redirect('/')



def zip_to_coord(zip_code):

    api_key = Config.gmaps_key
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_code}&key={api_key}"

    response = requests.get(url)
    response_json = json.loads(response.text)

    lat = response_json["results"][0]["geometry"]["location"]["lat"]
    longitude = response_json["results"][0]["geometry"]["location"]["lng"]
    return lat, longitude
