from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pytz

import pandas as pd
import pymysql
from datetime import datetime
import pytz
import random

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

        connected_database = db_config['database']  # Retrieve the database name from the db_config dictionary
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        table_names = [table[0] for table in cursor.fetchall()] #LIST COMPRENSION TO DISPLAY THE TABLES IN THAT DATABASE
        cursor.close()
        connection.close()
        return jsonify(status="Connected", database=connected_database, tables=table_names)
    except pymysql.Error as e:
        return jsonify(status="Error", message=str(e))


# To add data to report database
@app.route('/reports', methods=['POST'])
def add_report():
    data = request.json
    store_id = data.get('store_id')
    uptime_last_hour = data.get('uptime_last_hour')
    uptime_last_day = data.get('uptime_last_day')
    uptime_last_week = data.get('uptime_last_week')
    downtime_last_hour = data.get('downtime_last_hour')
    downtime_last_day = data.get('downtime_last_day')
    downtime_last_week = data.get('downtime_last_week')
    
    if not all([store_id, uptime_last_hour, uptime_last_day, uptime_last_week, downtime_last_hour, downtime_last_day, downtime_last_week]):
        return jsonify({'error': 'Missing required data'}), 400
    # Generate a random integer between 1 and 10
    report_id = random.randint(10000, 1000000)
    print(report_id)
    report = Report(
        store_id=store_id,
        uptime_last_hour=uptime_last_hour,
        uptime_last_day=uptime_last_day,
        uptime_last_week=uptime_last_week,
        downtime_last_hour=downtime_last_hour,
        downtime_last_day=downtime_last_day,
        downtime_last_week=downtime_last_week
    )
    
    db.session.add(report)
    db.session.commit()
    return jsonify({'message': 'Report added successfully' , 'report_id':report_id}), 201


#get report by id endpoint
@app.route('/get_report/<report_id>', methods=['GET'])
def get_report(report_id):
    try:
        report_by_id = Report.query.filter_by(id=report_id).first()       
        if report_by_id:
            report = {
            'report_id': report_by_id.id,
            'store_id' : report_by_id.store_id, 
            'uptime_last_hour': report_by_id.uptime_last_hour, 
            'uptime_last_day': report_by_id.uptime_last_week, 
            'update_last_week' : report_by_id.uptime_last_week, 
            'downtime_last_hour' : report_by_id.downtime_last_hour, 
            'downtime_last_day' : report_by_id.downtime_last_day, 
            'downtime_last_week': report_by_id.downtime_last_week
            }
            return jsonify({
                'message': 'Complete', 
                'report' : report
                }), 201

        else:
            return jsonify({'message': 'Report generating'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/trigger_report1', methods=['POST'])
def trigger_report1():
    store_id = request.form['store_id']
    return jsonify({
                'message': 'Complete', 
                'report' : store_id
                }), 201



class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, nullable=False)
    uptime_last_hour = db.Column(db.Integer, nullable=False, default=0)
    uptime_last_day = db.Column(db.Integer, nullable=False, default=0)
    uptime_last_week = db.Column(db.Integer, nullable=False, default=0)
    downtime_last_hour = db.Column(db.Integer, nullable=False, default=0)
    downtime_last_day = db.Column(db.Integer, nullable=False, default=0)
    downtime_last_week = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)



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
    timezone_str = db.Column(db.String(50), nullable=False)



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
