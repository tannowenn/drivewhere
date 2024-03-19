#!/usr/bin/env python3
import amqp_connection
import json
import pika
from os import environ
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import current_app

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root:root@localhost:3306/error'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Error(db.Model):
    __tablename__ = 'error'

    error_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    service = db.Column(db.String(32), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, code, message, service):
        self.code = code
        self.message = message
        self.service = service

    def json(self):
        return {
            'error_id': self.error_id,
            'code': self.code,
            'message': self.message,
            'service': self.service,
            'date_time': self.date_time,
        }

e_queue_name = environ.get('Error') or 'Error'

def receiveError(channel):
    try:
        channel.basic_consume(queue=e_queue_name, on_message_callback=callback, auto_ack=True)
        print('error microservice: Consuming from queue:', e_queue_name)
        channel.start_consuming()
    except pika.exceptions.AMQPError as e:
        print(f"error microservice: Failed to connect: {e}") 
    except KeyboardInterrupt:
        print("error microservice: Program interrupted by user.")

def callback(channel, method, properties, body):
    print("\nerror microservice: Received an error message")
    processError(body)

def processError(message):
    try:
        error_data = json.loads(message)
        code = error_data.get('code')
        message = error_data.get('message')
        service = error_data.get('service')

        if code is not None and message is not None and service is not None:
            with app.app_context():
                new_error = Error(code=code, message=message, service=service)
                db.session.add(new_error)
                db.session.commit()
                print("error microservice: Error message stored in the database successfully.")
        else: 
            print("error microservice: One or more fields are missing or null, skipping database insertion.")

    except Exception as e:
        print("error microservice: Failed to store error message in the database:", e)

if __name__ == "__main__":
    from threading import Thread

    web_server_thread = Thread(target=app.run, kwargs={"host":"0.0.0.0", "port":5005})
    web_server_thread.start()

    with app.app_context():
        print("error microservice: Getting Connection")
        connection = amqp_connection.create_connection()
        print("error microservice: Connection established successfully")
        channel = connection.channel()
        receiveError(channel)
    
