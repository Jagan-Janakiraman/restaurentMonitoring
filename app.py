from flask import Flask, jsonify, request, render_template
import pandas as pd
import mysql.connector
import pymysql
from mysql.connector import Error

app = Flask(__name__)

# Database configuration
db_config = {
    'host': '127.0.0.1:3306',
    'database': 'restaurent_monitoring',
    'user': 'root',
    'password': 'Password@123'
}    

# to create a database connection
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL database: {e}")
    return connection


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# to check the database connection
@app.route('/check_db_connection', methods=['GET'])
def check_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Password@123',
            database='restaurent_monitoring'
        )                               # Establish a connection to the database

        cursor = connection.cursor()    # Create a cursor object to execute SQL queries
        cursor.execute("SHOW TABLES")   # Execute a query to retrieve the table names in the database
        table_names = [table[0] for table in cursor.fetchall()]  # Fetch all the table names
        cursor.close()
        connection.close()              # Close the cursor and database connection
        return jsonify(status="Connected", tables=table_names)    # Return the table names as a response
    except pymysql.Error as e:
        return jsonify(status="Error", message=str(e))   # to  handle any database related   connection errors

if __name__ == '__main__':
    app.run(debug=True)
