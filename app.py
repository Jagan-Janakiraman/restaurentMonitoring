from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import mysql.connector

import pymysql
from mysql.connector import Error
from datetime import datetime
import pytz


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Password@123@localhost/restaurent_monitor'
db = SQLAlchemy(app)


# Database configuration
db_config = {
    'host': '127.0.0.1:3306',
    'database': 'restaurent_monitor',
    'user': 'root',
    'password': 'Password@123'
}

# to create a database connection
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL database: {e}")
    return connection


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
    store_status = db.Column(db.String(50), nullable=False)
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


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# to check the database connection
# to check the database connection
@app.route('/check_db_connection', methods=['GET'])
def check_db_connection():
    try:
        connection = create_connection()

        if connection is None:
            return jsonify(status="Error", message="Failed to connect to the database")

        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        table_names = [table[0] for table in cursor.fetchall()]
        database_name = connection.database  # Fetch the connected database name

        cursor.close()
        connection.close()

        return jsonify(status="Connected", database=database_name, tables=table_names)
    except pymysql.Error as e:
        return jsonify(status="Error", message=str(e))


@app.route('/get_report', methods=['GET'])
def get_report():
    try:
        report_id = request.args.get('report_id')
        report = Report.query.get(report_id)

        if report is None:
            return "Report not found"
        
        return report_id
    except Exception as e:
        return str(e)



if __name__ == '__main__':
    app.run(debug=True)
