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


# remember dont forget to change url if necessary and port no
# user_URL = environ.get('user_URL') or "http://localhost:5050/user/<string:owner_id>" 
rental_update_URL = environ.get('rental_update_URL') or "http://localhost:<PORTNO>/rental/update" 
rental_get_URL = environ.get('rental_get_URL') or "http://rental:<PORTNO>/rental "
payment_submit_URL = environ.get('payment_submit_URL') or "http://payment:4242/payment/rent" 
payment_release_URL = environ.get('payment_release_URL') or "http://payment:4242/payment/return"

# remember dont forget to change excahnge name
exchangename = environ.get('exchangename') or "master_topic" 
exchangetype = environ.get('exchangetype') or "topic" 

#create a connection and a channel to the broker to publish messages to error, email queues
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

# for user scenario 2
@app.route("/master/rental/request", methods=['POST'])
def rent_car():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            rental_request = request.get_json()
            print("\nReceived an rental_request in JSON:", rental_request)

            # order as follows
            # 1) goes to rental(get) to get owner id
            # 2) goes to user(get) to get owner email
            # 3) goes to payment(submit) to do payment
            # 4) goes to rental(put) to change rental status
            # 5) goes to email(amqp) to alert owner 
            
            #start get rental
            rental_get = getRental(rental_request)
            current_code = rental_get['code']
            
            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    
                    "message": "Failure at rental get service."
                }

            # starting get user
            owner_id = rental_get['data']
            user_get = getUser(owner_id)
            current_code = user_get['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    
                    "message": "Failure at user get service."
                }

            # start submit payment
            rental_id = rental_request['rentalId']
            payment_post = submitPayment(rental_id)
            current_code = payment_post['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    
                    "message": "Failure at submit payment service."
                }

            # start rental put
            rental_put = updateRental(rental_request)
            current_code = rental_put['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    
                    "message": "Failure at rental put service."
                }

            # start email amqp
            email_address = user_get['emailAddress']
            email_amqp = email(email_address)
            current_code = email_amqp['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    
                    "message": "Failure at email service."
                }

            # renturn everything success
            return {
                "code": 200,
                "message": "Everything was a success car is rented!"

            }
            

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
@app.route("/master/rental/update", methods=['PUT'])
def return_car():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            return_request = request.get_json()
            print("\nReceived an return_request in JSON:", return_request)
            
            # order as follows
            # 1) goes to rental(get) to get owner id
            # 2) goes to user(get) to get owner email+stripeid
            # 3) goes to payment(release) to do payment
            # 4) goes to rental(put) to change rental status
            # 5) goes to email(amqp) to alert owner 

            #start rental get
            rental_get = getRental(return_request)
            current_code = rental_get['code']
            
            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    
                    "message": "Failure at rental get service."
                }

            # start get user
            owner_id = rental_get['data']
            user_get = getUser(owner_id)
            current_code = user_get['code']
            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    
                    "message": "Failure at user get service."
                }

            # start release payment
            rental_id = return_request['rentalId']
            stripe_id = user_get['stripeId']
            payment_info = {
                "rentalId":rental_id,
                "stripeId":stripe_id
            }
            payment_post = releasePayment(payment_info)
            current_code = payment_post['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    
                    "message": "Failure at release payment service."
                }

            # start rental put
            rental_put = updateRental(return_request)
            current_code = rental_put['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    
                    "message": "Failure at rental put service."
                }

            # start email amqp
            email_address = user_get['emailAddress']
            email_amqp = email(email_address)
            current_code = email_amqp['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    
                    "message": "Failure at email service."
                }

            # return everything success
            return {
                "code": 200,
                "message": "Everything was a success car is returned!"

            }
            
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

# function to connect to payment service to submit payment
def submitPayment(rental_request):
    print('\n-----Invoking payment microservice-----')
    current_service = 'payment'
    payment_result = invoke_http(payment_submit_URL, method='POST', json=rental_request) 
    print('payment_result:', payment_result)

    # Check the payment result; if a failure, send it to the error microservice.
    code = payment_result["code"]

    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as payment fails-----')
        print('\n\n-----Publishing the (payment error) message with routing_key=payment.error-----')

        errorHandling(payment_result, code, current_service)
        
        return {
        "code": code,
        "data": {
            "payment_submit_result": payment_result,
        },
        "message": "Failure at payment_submit service."
    }
    else:
        return payment_result

# function to connect to payment service to submit payment
def releasePayment(rental_request):
    print('\n-----Invoking payment microservice-----')
    current_service = 'payment'
    payment_result = invoke_http(payment_release_URL, method='POST', json=rental_request)
    print('payment_result:', payment_result)

    # Check the payment result; if a failure, send it to the error microservice.
    code = payment_result["code"]
    
    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as payment fails-----')
        print('\n\n-----Publishing the (payment error) message with routing_key=payment.error-----')

        errorHandling(payment_result, code, current_service)

        return {
        "code": code,
        "data": {
            "payment_submit_result": payment_result,
        },
        "message": "Failure at payment_submit service."
    }
    else:
        return payment_result

# error handling function that is resused to save code
def errorHandling(result, code, current_service):
    message = json.dumps(result)
    channel.basic_publish(exchange=exchangename, routing_key=current_service+".error", 
        body=message, properties=pika.BasicProperties(delivery_mode = 2))

    print("\nservice status ({:d}) published to the RabbitMQ Exchange:".format(
        code), result)

    
    return {
        "code": 400,
        "data": {
            "result": result
        },
        "message": f"{current_service} error sent for error handling."
    }

# function for rental get list
def getRental(rental_request):

    # invoking rental microservice
    current_service = "rental"
    print('\n\n-----Invoking rental microservice-----')   

    rental_service_result = invoke_http(
        rental_get_URL, method="GET", json=rental_request)
    
    print("rental_status_result:", rental_service_result, '\n')

    # error handling for rental microservice
    code = rental_service_result["code"]
    if code not in range(200, 300):
        #send to error amqp and return stuff here
        errorHandling(rental_service_result, code, current_service)
        #below is return stuff instead of final return stuff
        return {
            "code": code,
            "data": {
                "rental_service_result": rental_service_result,
            },
            "message": "Failure at rental service."
        }
    else:
        return rental_service_result

# function for update rental
def updateRental(update_request):
    # invoking rental microservice
    current_service = "rental"
    print('\n\n-----Invoking rental microservice-----')    
    rental_service_result = invoke_http(
        rental_update_URL, method="PUT", json=update_request)
    print("rental_status_result:", rental_service_result, '\n')

    # error handling for rental microservice
    code = rental_service_result["code"]
    if code not in range(200, 300):
        #send to error amqp and return stuff here
        errorHandling(rental_service_result, code, current_service)
       
        return {
            "code": code,
            "data": {
                "rental_service_result": rental_service_result,
            },
            "message": "Failure at rental service."
        }
    else:
        return rental_service_result

# function for user service
def getUser(owner_id):
    # invoking user microservice
    current_service = "user"

    print('\n\n-----Invoking user microservice-----')    
    user_URL = f"http://localhost:5050/user/{owner_id}" 
    
    user_service_result = invoke_http(
        user_URL, method="GET")
    
    print("user_status_result:", user_service_result, '\n')

    # error handling for user microservice
    code = user_service_result["code"]
    if code not in range(200, 300):
        # do error amqp and return stuff
        errorHandling(user_service_result, code, current_service)
        
        return {
            "code": code,
            "data": {
                "user_service_result": user_service_result,
            },
            "message": "Failure at user service."
        }
    else:
        return user_service_result
    
# function for email
def email(email_address):
    # invoking amqp for email
    message = json.dumps(email_address)

    channel.basic_publish(exchange=exchangename, routing_key="email.alert", body=message, properties=pika.BasicProperties(delivery_mode = 2))
    # remember to ask if theres error for email amqp
    # remember to ask what routing key for email

    #remember how to determine if email success
    #remember will email service return anything?


if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for master microservice")
    app.run(host="0.0.0.0", port=5100, debug=True)
