from os import environ as env
from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_mysqldb import MySQL
from authlib.integrations.flask_client import OAuth
import mysql.connector
from mysql.connector import errorcode

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
app.config['MYSQL_HOST'] = env.get('MYSQL_HOST')
app.config['MYSQL_USER'] = env.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = env.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = env.get('MYSQL_DB')

cnx = mysql.connector.connect(
            user=env.get('MYSQL_USER'),
            password=env.get('MYSQL_PASSWORD'),
            host=env.get('MYSQL_HOST'),
            database=env.get('MYSQL_DB')
        )
mysql = MySQL(app)

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS mariohunt DEFAULT CHARACTER SET 'utf8'"
        )
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    # Use the database
    cursor.execute("USE mariohunt")

    # Create users table
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(100),
        password VARCHAR(255)
    )
    """
    cursor.execute(users_table)

    # Create characters table
    characters_table = """
    CREATE TABLE IF NOT EXISTS characters (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description VARCHAR(255) NOT NULL
    )
    """
    cursor.execute(characters_table)

def insert_values(cursor):
    # Check if users table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    
    if users_count == 0:
        # Insert values into users table
        users_insert = """
        INSERT INTO users (email, password) VALUES
        ('admin@mariohub.com', 'H3Y@dm!nH3Re#'),
        ('bowser@mariohub.com', 'Kidn@pth3princ3ss')
        """
        cursor.execute(users_insert)
    
    # Check if characters table is empty
    cursor.execute("SELECT COUNT(*) FROM characters")
    characters_count = cursor.fetchone()[0]
    
    if characters_count == 0:
        # Insert values into characters table
        characters_insert = """
    INSERT INTO characters (name, description) VALUES
    ('Mario', 'The main protagonist, Mario is a heroic plumber who often rescues Princess Peach from Bowser. Known for his red hat and blue overalls, he is cheerful, brave, and skilled in various sports and activities.'),
    ('Luigi', 'Mario’s younger brother, Luigi, is taller and wears green. Often portrayed as more timid, Luigi is equally heroic, having his own adventures, like in "Luigi''s Mansion."'),
    ('Princess Peach', 'The ruler of the Mushroom Kingdom, often kidnapped by Bowser. Princess Peach is kind and graceful, and she sometimes joins Mario on his adventures or rescues others herself.'),
    ('Bowser', 'The main antagonist, Bowser is the King of the Koopas. He frequently kidnaps Princess Peach in his quest to conquer the Mushroom Kingdom. Bowser is powerful and often battles Mario.'),
    ('Yoshi', 'Yoshi is a friendly dinosaur and loyal companion to Mario. Known for his long tongue and ability to eat enemies, Yoshi often helps Mario on his quests and has his own series of adventures.'),
    ('Toad', 'A loyal attendant of Princess Peach, Toad is known for his mushroom-like appearance. He often assists Mario and has his own adventures, showing bravery despite his small size.'),
    ('Donkey Kong', 'Originally an antagonist, Donkey Kong is a powerful ape who has become a hero in his own right. He is known for his strength and love of bananas, starring in his own series of games.'),
    ('Princess Daisy', 'The tomboyish princess of Sarasaland, Daisy is a friend of Princess Peach. She is energetic, sporty, and often appears in various Mario sports and party games.'),
    ('Wario', 'Wario is Mario’s greedy and mischievous rival. Known for his yellow and purple outfit, Wario stars in his own series of games focused on treasure hunting and quirky minigames.'),
    ('Bowser Jr.', 'Bowser’s son, Bowser Jr. often assists his father in his schemes to capture Princess Peach and defeat Mario. He is mischievous but loyal to his father, appearing in many Mario games.'),
    ('Toadette', 'A cheerful and adventurous Toad, Toadette is often seen helping Princess Peach and Toad. She is known for her pink pigtails and appears in various Mario games.'),
    ('Koopa Troopa', 'A common enemy in the Mario series, Koopa Troopas are turtle-like creatures that come in various colors. They are loyal to Bowser but are also seen as playable characters in spin-off games.')
    """
        cursor.execute(characters_insert)


if __name__ == '__main__':
    from controllers.routes import app
    cursor = cnx.cursor()
    create_database(cursor)
    create_tables(cursor)
    insert_values(cursor)
    cnx.commit()
    cursor.close()
    cnx.close()
    app.run(debug=True, host='0.0.0.0', port=5000)