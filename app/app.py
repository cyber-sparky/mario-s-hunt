import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, send_from_directory, request, render_template_string
from flask_mysqldb import MySQL
from functools import wraps

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)
LocalStorageAdmin = "580c968a1ae80a6577c15c48d2c7af74"
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root@123'
app.config['MYSQL_DB'] = 'mariohunt'

mysql = MySQL(app)

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
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    user = session.get("user")  # Retrieve user information from session
    if user is None:
        return "Unauthorized"
    return render_template('dashboard.html', user=user, USERNAME=env.get("USERNAME"))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('adminLogin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/adminLogin", methods=["GET", "POST"])
def adminLogin():
    session.clear()
    if request.method == "POST":
        email = request.form["email"]
        password = request.form['password']
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            admin_user = cur.fetchone()
            cur.close()

            if admin_user:
                session["admin_logged_in"] = True
                session["name"] = email
                session["login_success"] = True  # Set the flag for successful login
                return redirect(url_for("admin"))
            else:
                session["admin_logged_in"] = False
                return render_template('adminLogin.html', error="Invalid credentials, please try again.")
        except Exception as e:
            return f"An error occurred: {str(e)}"
        
    return render_template('adminLogin.html')


@app.route("/admin", methods=["GET", "POST"])
def admin():
    print(session.get("admin_logged_in"))
    if session.get("admin_logged_in") == False:
        print("inside if")
        return redirect(url_for("adminLogin"))

    if request.method == "POST":
        submitted_data = [
            {"category": request.form.get("category1"), "value": request.form.get("value1")},
            {"category": request.form.get("category2"), "value": request.form.get("value2")},
            {"category": request.form.get("category3"), "value": request.form.get("value3")}
        ]
        return render_template('admin.html', submitted_data=submitted_data, raw_input=request.form)
    

    return render_template('admin.html', submitted_data=None, raw_input=None)

@app.route("/adminUpdate", methods=["GET","POST"])
def admin_update():
    # Get URL parameters
    category1 = request.form.get("category1")
    category2 = request.form.get("category2")
    category3 = request.form.get("category3")
    value1 = request.form.get("value1")
    value2 = request.form.get("value2")
    value3 = request.form.get("value2")
     # Read the contents of the header.html file
    with open('templates/header.html') as header_file:
        header_html = header_file.read()
    with open('templates/aside.html') as aside_file:
        aside_html = aside_file.read()

    base_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Admin Update</title>
        <link rel="stylesheet" href="../static/css/allpage.css" />
        <link rel="stylesheet" href="../static/css/dashboard.css" />
    </head>
    <body>
    ''' + header_html + '''
        <main>
            <img src="../static/images/background.jpg" alt="backgroundImage" class="backgroundImage" />
            ''' + aside_html + '''
            <section>
                <div class="submittedContent">
                    <div class="submittedData">
                        <h3>Updated Mario Powers</h3>
                        <table>
                            <tr>
                                <td>{}</td>
                                <td>{}</td>
                            </tr>
                             <tr>
                                <td>{}</td>
                                <td>{}</td>
                            </tr>
                             <tr>
                                <td>{}</td>
                                <td>{}</td>
                            </tr>
                        </table>
                        <form action="/admin" method="get" class="reenterBtn">
                            <button type="submit" class="btn btn-primary">Reenter</button>
                        </form>
                    </div>
                 
                </div>
            </section>
        </main>
    </body>
    </html>
    '''.format(category1,value1,category2,value2,category3,value3)
    return render_template_string(base_template)

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

@app.route("/search_character")
def search_character():
    name = request.args.get('name', '')
    try:
        cur = mysql.connection.cursor()
        query = f"SELECT id, name, description FROM characters WHERE name LIKE '%{name}%'"
        #mario%' UNION SELECT id,email,password FROM users;#
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        user = session.get("user")  # Retrieve user information from session
        return render_template('characters.html', results=results, user=user, USERNAME=env.get("USERNAME"))
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        user = session.get("user") 
        return render_template('characters.html', error=error_message, user=user, USERNAME=env.get("USERNAME"))

@app.route("/")
def home():
    return render_template('maintenance.html')

@app.route("/characters")
def characters():
    user = session.get("user")  # Retrieve user information from session
    return render_template('characters.html', user=user, USERNAME=env.get("USERNAME"))

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
    return render_template('confidential/username.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)