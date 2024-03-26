#!/usr/bin/env python3
import error.amqp_connection as amqp_connection
import json
import pika
#from os import environ

from os import environ
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/error'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

CORS(app)  

class Error(db.Model):
    __tablename__ = 'error'

    error_id = db.Column(db.Integer, primary_key=True)
    errorMsg = db.Column(db.String(32), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, error_id, errorMsg, date_time):
        self.error_id = error_id
        self.errorMsg = errorMsg
        self.date_time = date_time

    def json(self):
        dto = {
            'error_id': self.error_id,
            'errorMsg': self.errorMsg,
            'date_time': self.date_time,
        }

        return dto


e_queue_name = environ.get('Error') or 'Error' #Error

def receiveError(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=e_queue_name, on_message_callback=callback, auto_ack=True)
        print('error microservice: Consuming from queue:', e_queue_name)
        channel.start_consuming() # an implicit loop waiting to receive messages; 
        #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
    except pika.exceptions.AMQPError as e:
        print(f"error microservice: Failed to connect: {e}") 

    except KeyboardInterrupt:
        print("error microservice: Program interrupted by user.")

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nerror microservice: Received an error by " + __file__)
    processError(body)
    print()

def processError(errorMsg):
    print("error microservice: Printing the error message:")
    try:
        error = json.loads(errorMsg)
        print("--JSON:", error)
    except Exception as e:
        print("--NOT JSON:", e)
        print("--DATA:", errorMsg)
    print()

if __name__ == "__main__": # execute this program only if it is run as a script (not by 'import')   
    print("This is flask for " + os.path.basename(__file__) + ": error ...")
    app.run(host='0.0.0.0', port=5001, debug=True)

    print("error microservice: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("error microservice: Connection established successfully")
    channel = connection.channel()
    receiveError(channel)

