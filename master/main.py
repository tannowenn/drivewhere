from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http

import pika
import json
import amqp_connection

app = Flask(__name__)
CORS(app)


# dont forget to change url if necessary
user_URL = environ.get('user_URL') or "http://localhost:<PORTNO>/user" 
rental_URL = environ.get('rental_URL') or "http://localhost:<PORTNO>/rental" 
payment_URL = environ.get('payment_URL') or "http://localhost:<PORTNO>/payment" 

#dont forget to change excahnge name
exchangename = environ.get('exchangename') or "amqp_topic" 
exchangetype = environ.get('exchangetype') or "topic" 

#create a connection and a channel to the broker to publish messages to error, email queues
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

# for user scenario 2
@app.route("/master/main", methods=['POST'])
def rent_car():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            rental_request = request.get_json()
            print("\nReceived an rental_request in JSON:", rental_request)

            # do the actual work
            # 1. Send rental request
            pay_result = processPayment(rental_request)
            if pay_result == True:
                result = processMain(rental_request)
                
            else:
                return {
                    "code": 500,
                    "data": {"payment_result": 'failed'},
                    "message": "Payment failure sent for error logging."
                }
                # print(pay_result) # remember if its above return or print result
            
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "master/main.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

# for user scenario 3
@app.route("/master/main", methods=['PUT'])
def return_car():
    return

# function to connect to payment service
def processPayment(rental_request):
    print('\n-----Invoking payment microservice-----')
    payment_result = invoke_http(payment_URL, method='POST', json=rental_request) # remember to find out what method, for now i use post
    print('payment_result:', payment_result)

    # Check the payment result; if a failure, send it to the error microservice.
    code = payment_result["code"]
    message = json.dumps(payment_result)

    # remember to ask if complex master need to go to amqp or go to error micro(then error goes to amqp)
    if code not in range(200, 300): # remember to find what code error uses to be an error
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as payment fails-----')
        print('\n\n-----Publishing the (payment error) message with routing_key=payment.error-----')

        channel.basic_publish(exchange=exchangename, routing_key="payment.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) # remember to find out whats the error routing key i suggest they use *.error

        print("\nPayment status ({:d}) published to the RabbitMQ Exchange:".format(
            code), payment_result)
        
        return {
            "code": 500,
            "data": {"payment_result": payment_result},
            "message": "Payment failure sent for error logging."
        }
    else:
        return True

# error handling function that is resused to save code
def errorHandling(result, code, current_service):
    message = json.dumps(result)
    channel.basic_publish(exchange=exchangename, routing_key=current_service+".error", 
        body=message, properties=pika.BasicProperties(delivery_mode = 2))# remember idk if can combine var with str in routing key

    print("\nservice status ({:d}) published to the RabbitMQ Exchange:".format(
        code), result)

    # 7. Return error
    return {
        "code": 400,
        "data": {
            "result": result
        },
        "message": f"Simulated {current_service} error sent for error handling."
    }

# function for processes of scenario 2 and 3
def processMain(rental_request):
    #user
    #rental
    #amqp(email)

    # invoking rental microservice
    current_service = "rental"
    print('\n\n-----Invoking rental microservice-----')    
    rental_service_result = invoke_http(
        rental_URL, method="PUT", json=rental_request)
    print("rental_status_result:", rental_service_result, '\n')

    # error handling for rental microservice
    code = rental_service_result["code"]
    if code not in range(200, 300):
        return errorHandling(rental_service_result, code, current_service)
    
    # invoking user microservice
    current_service = "user"
    print('\n\n-----Invoking user microservice-----')    
    user_service_result = invoke_http(
        user_URL, method="GET", json=rental_service_result)
    print("user_status_result:", user_service_result, '\n')

    # error handling for user microservice
    code = user_service_result["code"]
    if code not in range(200, 300):
        return errorHandling(user_service_result, code, current_service)
    
    # invoking amqp for email
    message = json.dumps(user_service_result)

    channel.basic_publish(exchange=exchangename, routing_key="order.info", body=message)
    # remember to ask if theres error for email amqp

    # everything successful, u got rental, user and emailed
    return {
        "code": 201,
        "data": {
            "rental_service_result": rental_service_result,
            "user_service_result": user_service_result,
            "emailed_already":True
        }
    }

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    app.run(host="0.0.0.0", port=5100, debug=True)