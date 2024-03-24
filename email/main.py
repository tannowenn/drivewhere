import amqp_connection
import json
import pika
import ssl
import smtplib

from os import environ
from email.message import EmailMessage

GMAIL_APP_PASS = environ.get('GMAIL_APP_PASS')
EMAIL_SENDER = "drivewhere1@gmail.com"

a_queue_name = environ.get('a_queue_name') or 'Email' # queue to be subscribed by Email microservice

def send_email(email_receiver, subject, body):

    em = EmailMessage()
    em['From'] = EMAIL_SENDER
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, GMAIL_APP_PASS)
        smtp.sendmail(EMAIL_SENDER, email_receiver, em.as_string())

def send_scenario_email(email_receiver, scenario, receiver_role):
    signoff = """Regards,\nDriveWhere"""

    scenario_content = {
        "rent": {
            "renter": {
                "subject": "Successfully rented a car!",
                "body": f"""Dear {email_receiver.split("@")[0]},

Received confirmation for your car rental. Enjoy your drive, and thank you for using DriveWhere!
This is an automated email. Please do not reply to this email address as it is not a monitored mailbox.

{signoff}"""
            },
            "owner": {
                "subject": "Successfully rent out a car!",
                "body": f"""Dear {email_receiver.split("@")[0]},

Your car rent out process is a success. Thank you for using DriveWhere!
This is an automated email. Please do not reply to this email address as it is not a monitored mailbox.

{signoff}"""
            }
        },
        "return": {
            "renter": {
                "subject": "Successfully returned the rented car!",
                "body": f"""Dear {email_receiver.split("@")[0]},

Your car return process is a success. Thank you for using DriveWhere!
This is an automated email. Please do not reply to this email address as it is not a monitored mailbox.

{signoff}"""
            },
            "owner": {
                "subject": "Successfully received your returned car!",
                "body": f"""Dear {email_receiver.split("@")[0]},

Received confirmation for the return of your car. You may proceed list the car if you wish to rent it out again. Thank you for using DriveWhere!
This is an automated email. Please do not reply to this email address as it is not a monitored mailbox.

{signoff}"""
            }
        }
    }
    send_email(email_receiver=email_receiver, subject=scenario_content[scenario][receiver_role]["subject"], body=scenario_content[scenario][receiver_role]["body"])

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
    renter_email = email_data.get('renterEmailAddress')
    owner_email = email_data.get('ownerEmailAddress')
    scenario = email_data.get('scenario')
    if email_data is not None:
        send_scenario_email(email_receiver=renter_email, scenario=scenario, receiver_role="renter")
        send_scenario_email(email_receiver=owner_email, scenario=scenario, receiver_role="owner")
    else:
        print("Invalid JSON format. Missing 'code' or 'message' field.")

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("email address: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("email address: Connection established successfully")
    channel = connection.channel()
    receiveEmailAdd(channel)
