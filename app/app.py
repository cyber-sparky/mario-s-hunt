import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, send_from_directory

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    user_info = oauth.auth0.parse_id_token(token, nonce=None)
    session["user"] = user_info
    print(user_info)
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "return_to": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/")
def home():
    return render_template('maintenance.html')

@app.route('/robots.txt')
def robots_txt():
    return send_from_directory(app.root_path, 'robots.txt')

@app.route("/confidential", methods=["GET"])
def confidential():
    return render_template('confidential/confidential.html')

@app.route('/r')
def show_message_r():
    return "<h1>Oh You came here to find anything, Nahh not here</h1> "

@app.route('/r/a/')
def show_message_r_a():
    return "<h1>Hmmm... I see.. You're trying to do something, aren't you ?</h1>"
@app.route('/r/a/b/')
def show_message_r_a_b():
    return "<h1>now what ? dig deeper</h1>"

@app.route('/r/a/b/b/')
def show_message_r_a_b_b():
    return "<h1>This is not good, you're coming too close</h1>"

@app.route('/r/a/b/b/i/')
def show_message_r_a_b_b_i():
    return "<h1>Hey you are one step close to me</h1>"

@app.route('/r/a/b/b/i/t/')
def show_message_r_a_b_b_i_t():
    return render_template('username.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)