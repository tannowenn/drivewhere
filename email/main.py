import amqp_connection
import json
import pika
import ssl
import smtplib

from os import environ
from email.message import EmailMessage

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from datetime import datetime

GMAIL_APP_PASS = environ.get('GMAIL_APP_PASS')
EMAIL_SENDER = "drivewhere1@gmail.com"

# app = Flask(__name__)
# CORS(app)

a_queue_name = environ.get('a_queue_name') or 'Email' # queue to be subscribed by Email microservice

def send_email(email_receiver, subject, body):
    # email_receiver = "owen.tan.2022@scis.smu.edu.sg"
    # subject = "TEST SUbejsdt"
    # body = """
    # Hello this is the test email abadljaladjbjalbjad@#$@!
    # """

    em = EmailMessage()
    em['From'] = EMAIL_SENDER
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, GMAIL_APP_PASS)
        smtp.sendmail(EMAIL_SENDER, email_receiver, em.as_string())

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
    print("\nEmail Address: Received an email by " + __file__)
    processEmailAdd(body)
    print()

def processEmailAdd(email):
    email_data = json.loads(email)
    emailAdd = email_data.get('email')
    if emailAdd is not None:
        print(f"Email Address: {emailAdd}")
    else:
        print("Invalid JSON format. Missing 'code' or 'message' field.")

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("email address: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("email address: Connection established successfully")
    channel = connection.channel()
    receiveEmailAdd(channel)
