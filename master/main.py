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


rental_update_URL = environ.get('rental_update_URL') or "http://host.docker.internal:5002/rental/update" 
rental_get_URL = environ.get('rental_get_URL') or "http://host.docker.internal:5002/rental/info"

payment_submit_URL = environ.get('payment_submit_URL') or "http://host.docker.internal:5004/payment/rent" 
payment_release_URL = environ.get('payment_release_URL') or "http://host.docker.internal:5004/payment/return"

# remember dont forget to change excahnge name
exchangename = environ.get('exchangename') or "Error" 
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

            renterID = rental_request["userId"]
            paymentAmt = rental_request["paymentAmt"]
            rentalId = rental_request["rentalId"]
            
            #start get rental
            sendData = {
                "rentalId":rentalId
            }
            rental_get = getRental(sendData)
            current_code = rental_get['code']
            
            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": rental_get["data"],
                    "message": "Failure at rental get service."
                }
            ownerId = rental_get['data']['userId']
            
            # starting get user
            user_get = getUser(ownerId)
            current_code = user_get['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": user_get["data"],
                    "message": "Failure at user get service."
                }
            email_address = user_get['data']['emailAddress']
            print(email_address)
            # # start submit payment
            # sub_pay = {
            #     "rentalId": rentalId,
            #     "paymentAmt": paymentAmt,
            #     "payerId": renterID,
            #     "payeeId": ownerId
            # }

            # payment_post = submitPayment(sub_pay)
            # current_code = payment_post['code']

            # if current_code not in range(200, 300):
            #     #no need send to error amqp as its done already and return stuff here
            #     return {
            #         "code": current_code,
            #         "data": payment_post["data"],
            #         "message": "Failure at payment submit"
            #     }


            # start rental put
            sendData2 = {
                "rentalId": rentalId,
                "status": "rented"
            }
            
            rental_put = updateRental(sendData2)
            current_code = rental_put['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": rental_put["data"],
                    "message": "Failure at rental put service."
                }

            # # start email amqp
            # email_amqp = email(email_address)
            # current_code = email_amqp['code']

            # if current_code not in range(200, 300):
            #     #no need send to error amqp as its done already and return stuff here
                
            #     return {
            #         "code": current_code,
            
            #         "message": "Failure at email service."
            #     }

            # renturn everything success
            return {
                "code": 200,
                "message": "Everything is a success, car is rented"

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

            rentalId = return_request["rentalId"]

            #start rental get
            sendData = {
                "rentalId":rentalId
            }

            rental_get = getRental(sendData)
            current_code = rental_get['code']
            
            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": rental_get["data"],
                    "message": "Failure at rental get service."
                }
            
            ownerId = rental_get['data']['userId']
            
            # start get user
            user_get = getUser(ownerId)
            current_code = user_get['code']
            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": user_get["data"],
                    "message": "Failure at user get service."
                }
            email_address = user_get['data']['emailAddress']
            stripeId =  user_get['data']['stripeId']

            # # start release payment
            # payment_info = {
            #     "rentalId": rentalId,
            #     "stripeId": stripeId
            # }
            # payment_post = releasePayment(payment_info)
            # current_code = payment_post['code']

            # if current_code not in range(200, 300):
            #     #no need send to error amqp as its done already and return stuff here
                
            #     return {
            #         "code": current_code,
            #         "data": payment_post,
            #         "message": "Failure at release payment service."
            #     }

            # start rental put
            sendData2 = {
                "rentalId": rentalId,
                "status": "finishedRent"
            }

            rental_put = updateRental(sendData2)
            current_code = rental_put['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": rental_put["data"],
                    "message": "Failure at rental put service."
                }

            # # start email amqp
            # email_amqp = email(email_address)
            # current_code = email_amqp['code']

            # if current_code not in range(200, 300):
            #     #no need send to error amqp as its done already and return stuff here
                
            #     return {
            #         "code": current_code,
                    
            #         "message": "Failure at email service."
            #     }

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
def submitPayment(sub_pay):
    print('\n-----Invoking payment microservice-----')
    current_service = 'payment'
    payment_result = invoke_http(payment_submit_URL, method='POST', json=sub_pay) 
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
        "data": payment_result,
    }
    else:
        return payment_result

# # function to connect to payment service to submit payment
# def releasePayment(rental_request):
#     print('\n-----Invoking payment microservice-----')
#     current_service = 'payment'
#     payment_result = invoke_http(payment_release_URL, method='POST', json=rental_request)
#     print('payment_result:', payment_result)

#     # Check the payment result; if a failure, send it to the error microservice.
#     code = payment_result["code"]
    
#     if code not in range(200, 300):
#         # Inform the error microservice
#         #print('\n\n-----Invoking error microservice as payment fails-----')
#         print('\n\n-----Publishing the (payment error) message with routing_key=payment.error-----')

#         errorHandling(payment_result, code, current_service)

#         return {
#         "code": code,
#         "data": payment_result,
#     }
#     else:
#         return payment_result

# error handling function that is resused to save code
def errorHandling(result, code, current_service):
    print('\n\n-----Invoking error handling-----')
    co_de = result['code']
    mes_sage = result['message']  

    result = {
        'code': co_de,
        'message': mes_sage,
        'service': current_service
    }

    message = json.dumps(result)
    print(message)
    channel.basic_publish(exchange=exchangename, routing_key=current_service+".error", 
        body=message, properties=pika.BasicProperties(delivery_mode = 2))
    print("\nservice status ({:d}) published to the RabbitMQ Exchange:".format(
        code), result)

    
    return {
        "code": 400,
        "data": result,
        "message": f"{current_service} error sent for error handling."
    }

# function for rental get list
def getRental(sendData):

    # invoking rental microservice
    current_service = "rental"
    print('\n\n-----Invoking get rental microservice-----')   
    
    rental_service_result = invoke_http(
        rental_get_URL, method="GET", json=sendData)
    
    print("rental_status_result:", rental_service_result, '\n')

    # error handling for rental microservice
    code = rental_service_result["code"]
    if code not in range(200, 300):
        #send to error amqp and return stuff here
        errorHandling(rental_service_result, code, current_service)
        #below is return stuff instead of final return stuff
        return {
            "code": code,
            "data": rental_service_result
        }
    else:
        return rental_service_result

# function for update rental
def updateRental(update_request):
    # invoking rental microservice
    current_service = "rental"
    print('\n\n-----Invoking put rental microservice-----')    
    rental_service_result = invoke_http(rental_update_URL, method="PUT", json=update_request)
    print("rental_status_result:", rental_service_result, '\n')

    # error handling for rental microservice
    code = rental_service_result["code"]
    if code not in range(200, 300):
        #send to error amqp and return stuff here
        errorHandling(rental_service_result, code, current_service)
       
        return {
            "code": code,
            "data": rental_service_result,
        }
    else:
        return rental_service_result

# function for user service
def getUser(owner_id):
    # invoking user microservice
    current_service = "user"

    print('\n\n-----Invoking user microservice-----')    
    user_URL = f"http://user:5001/user/{owner_id}" 
    
    user_service_result = invoke_http(
        user_URL, method="GET", json={})
    
    print("user_status_result:", user_service_result, '\n')

    # error handling for user microservice
    code = user_service_result["code"]
    if code not in range(200, 300):
        # do error amqp and return stuff
        errorHandling(user_service_result, code, current_service)
        
        return {
            "code": code,
            "data": user_service_result
        }
    else:
        return user_service_result
    
# # function for email
# def email(email_address):
#     # invoking amqp for email
#     message = json.dumps(email_address)

#     channel.basic_publish(exchange=exchangename, routing_key="email.alert", body=message, properties=pika.BasicProperties(delivery_mode = 2))
#     # remember to ask if theres error for email amqp
#     # remember to ask what routing key for email

#     #remember how to determine if email success
#     #remember will email service return anything?


if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for master microservice")
    app.run(host="0.0.0.0", port=5100, debug=True)
