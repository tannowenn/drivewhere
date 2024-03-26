#!/usr/bin/env python3
import amqp_connection
import json
import pika
from os import environ

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

app = Flask(__name__)
CORS(app)

a_queue_name = environ.get('a_queue_name') or 'Email' # queue to be subscribed by Email microservice


def receiveEmailAdd(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=a_queue_name, on_message_callback=callback, auto_ack=True)
        print('email address: Consuming from queue:', a_queue_name)
        channel.start_consuming()  # an implicit loop waiting to receive messages;
             #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
    except pika.exceptions.AMQPError as e:
        print(f"email address: Failed to connect: {e}") # might encounter error if the exchange or the queue is not created

    except KeyboardInterrupt:
        print("email address: Program interrupted by user.") 


def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nemail address: Received an email by " + __file__)
    processEmailAdd(json.loads(body))
    print()

def processEmailAdd(order):
    print("email address: Printing an email:")
    print(order)

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("email address: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("email address: Connection established successfully")
    channel = connection.channel()
    receiveEmailAdd(channel)
