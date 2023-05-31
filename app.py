from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/restaurent_monitor'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database configuration
db_config = {
    'host': 'localhost',
    'database': 'restaurent_monitor',
    'user': 'root',
    'password': 'password'
}

# to create a database connection
def create_connection():
    connection = None
    try:
        connection = pymysql.connect(**db_config)
        # print("Connected to MySQL database")
        return connection
    except pymysql.Error as e:
        print(f"Error while connecting to MySQL database: {e}")
    return connection


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# to check the database connection
@app.route('/check_db_connection', methods=['GET'])
def check_db_connection():
    try:
        connection = create_connection()
        if connection is None:
            return jsonify(status="Error", message="Failed to connect to the database")

        connected_database = connection.database
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        table_names = [table[0] for table in cursor.fetchall()]
        cursor.close()
        connection.close()
        return jsonify(status="Connected", database=connected_database, tables=table_names)
    except pymysql.Error as e:
        return jsonify(status="Error", message=str(e))


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, nullable=False)
    # Other columns and model definitions


class StoreStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, nullable=False)
    store_status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class BusinessHours(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    start_time_local = db.Column(db.DateTime, default=datetime.utcnow)
    end_time_local = db.Column(db.DateTime, default=datetime.utcnow)


class Timezone(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, nullable=False)
    timezone = db.Column(db.String(50), nullable=False)

    def __init__(self, store_id):
        self.store_id = store_id
        self.timezone = self.get_local_timezone()

    def get_local_timezone(self):
        return datetime.now(pytz.timezone("UTC")).astimezone().tzinfo.zone


if __name__ == '__main__':
    app.run(debug=True)
