from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

import os, sys
from os import environ

from invokes import invoke_http

import pika
import json
import amqp_connection

app = Flask(__name__)
CORS(app)

PORT = environ.get('PORT') or 5100
FRONTEND_HOST = environ.get('FRONTEND_HOST') or "localhost"
PAYMENT_HOST = environ.get('PAYMENT_HOST') or "payment"
PAYMENT_PORT = environ.get('PAYMENT_PORT') or 5004
rental_update_URL = environ.get('rental_update_URL') or "http://host.docker.internal:5002/rental/update" 
rental_get_URL = environ.get('rental_get_URL') or "http://host.docker.internal:5002/rental/info"
rental_list_URL = environ.get('rental_list_URL') or "http://host.docker.internal:5002/rental"

user_get_URL = environ.get('user_get_URL') or "http://host.docker.internal:5001/user"

payment_submit_URL = environ.get('payment_submit_URL') or "http://host.docker.internal:5004/payment/rent" 
payment_release_URL = environ.get('payment_release_URL') or "http://host.docker.internal:5004/payment/return"

# remember dont forget to change exchange name
exchangename = environ.get('exchangename') or "drivewhere_topic" 
exchangetype = environ.get('exchangetype') or "topic" 

#create a connection and a channel to the broker to publish messages to error, email queues
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

# for user scenario 2 part 1
@app.route("/master/rental", methods=['POST'])
def get_rental():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            data = request.get_json()
            rental_response = listRental(data)
            current_code = rental_response['code']
            
            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": rental_response["data"],
                    "message": "Failure at rental get service."
                }
            rental_list = rental_response["data"]["rental_list"]

            user_response = getAllUsers()
            current_code = user_response['code']
            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": user_response["data"],
                    "message": "Failure at get all user service."
                }
            user_list = user_response["data"]["users"]
            user_phone_dict = {}
            for user in user_list:
                user_phone_dict[str(user['userId'])] = user['phoneNum']

            for rental in rental_list:
                try:
                    rental['phoneNum'] = user_phone_dict[str(rental['userId'])]
                except KeyError:
                    return jsonify({
                        "code": 500,
                        "message": f"Error getting phone num of user ID {rental['userId']}, maybe user ID does not exist in user DB?"
                    }), 500
            
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "rental_list": rental_list
                    }
                }
            )

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


# for user scenario 2 part 2
@app.route("/master/rental/request", methods=['POST'])
def rent_car():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            rental_request = request.get_json()
            print("\nReceived an rental_request in JSON:", rental_request)
            
            # order as follows
            # 1) goes to rental(get) to get owner id and payment amt
            # 2) goes to user(get) to get owner email
            # 3) goes to user(get) to get renter email
            # 4) goes to payment(submit) to do payment

            renterID = rental_request["userId"]
            days = rental_request["days"]
            rentalId = rental_request["rentalId"]
            
            #start get rental
            sendData = {
                "rentalId":rentalId,
                "days": days
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
            paymentAmt = int(rental_get['data']['PaymentAmount'])

            # starting get user to get owner email
            user_get_owner = getUser(ownerId)
            current_code = user_get_owner['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": user_get_owner["data"],
                    "message": "Failure at user get service."
                }
            
            ownerEmailAddress = user_get_owner['data']['emailAddress']
            print(ownerEmailAddress)

            # starting get user to get renter email
            user_get_renter = getUser(renterID)
            current_code = user_get_renter['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": user_get_renter["data"],
                    "message": "Failure at user get service."
                }
            
            renterEmailAddress = user_get_renter['data']['emailAddress']
            print(renterEmailAddress)

            # start submit payment
            sub_pay = {
                "rentalId": rentalId,
                "paymentAmt": paymentAmt,
                "payerId": renterID,
                "payeeId": ownerId,
                "ownerEmailAddress": ownerEmailAddress, 
                "renterEmailAddress": renterEmailAddress,
            }

            payment_post = submitPayment(sub_pay)
            current_code = payment_post['code']
            
            if current_code not in range(200, 399):
                #no need send to error amqp as its done already and return stuff here
                return{
                    "code": current_code,
                    "data": payment_post["data"],
                    "message": "Failure at payment submit"
                }
            else:
                print("\nSending to the checkout page now")
                return jsonify({
                    "code": 200,
                    "data": {"url": payment_post['redirect_url']}
                }), 200
            
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

# continued scenario 2
@app.route("/master/rental/continue", methods=['GET'])
def continued():
    try:
        session_id = request.args.get('session_id')
        rental_id = request.args.get('rental_id')
        payer_id = request.args.get('payer_id')
        payee_id = request.args.get('payee_id')
        renter_email_address = request.args.get('renter_email_address')
        owner_email_address = request.args.get('owner_email_address')
        
        payment_response = invoke_http(f"http://{PAYMENT_HOST}:{PAYMENT_PORT}/payment/success?rental_id={rental_id}&payer_id={payer_id}&payee_id={payee_id}&session_id={session_id}")
        current_code = payment_response["code"]

        print("\nContinuing rental_request")

        # 5) goes to rental(put) to change rental status to rented
        # 6) goes to email(amqp) to alert owner and renter

        if current_code not in range(200, 399):
            #no need send to error amqp as its done already and return stuff here
            errorHandling(payment_response, current_code, "payment")
            return{
                "code": current_code,
                "data": payment_response,
                "message": "Failure at payment submit"
            }
        
        rentalId = rental_id
        ownerEmailAddress = owner_email_address
        renterEmailAddress = renter_email_address
        
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

        # start email amqp
        result = {
            'renterEmailAddress': renterEmailAddress,
            'ownerEmailAddress': ownerEmailAddress,
            'scenario': "rent"
        }
        email_amqp = email(result)

        # renturn everything success
        # return {
        #     "code": 200,
        #     "message": "Everything is a success, car is rented",
        #     "data": {"redirect_url": f"http://{FRONTEND_HOST}/frontend/index.html"}
        # }            
        return redirect(f"http://{FRONTEND_HOST}/frontend/index.html")

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

@app.route("/master/rental/cancel")
def cancel():
    return redirect(f"http://{FRONTEND_HOST}/frontend/index.html")

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
            # 3) goes to payment(release) to do payment and receive renter user id
            # 4)goes to user(get) to get renter email
            # 5) goes to rental(put) to change rental status
            # 6) goes to email(amqp) to alert owner 

            rentalId = return_request["rentalId"]

            #start rental get
            sendData = {
                "rentalId": rentalId,
                "days": 0
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
            
            # starting get user to get owner email and stripe id
            user_get_owner = getUser(ownerId)
            current_code = user_get_owner['code']
            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": user_get_owner["data"],
                    "message": "Failure at user get service."
                }
            ownerEmailAddress = user_get_owner['data']['emailAddress']
            print(ownerEmailAddress)
            stripeId =  user_get_owner['data']['stripeId']

            # start release payment
            payment_info = {
                "rentalId": rentalId,
                "stripeId": stripeId
            }
            payment_post = releasePayment(payment_info)
            current_code = payment_post['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": payment_post,
                    "message": "Failure at release payment service."
                }
            
            print("\nreleased payment data")
            print(payment_post["data"])
            renterId = payment_post["data"]["payerId"]

            # starting get user to get renter email
            user_get_renter = getUser(renterId)
            current_code = user_get_renter['code']

            if current_code not in range(200, 300):
                #no need send to error amqp as its done already and return stuff here
                
                return {
                    "code": current_code,
                    "data": user_get_renter["data"],
                    "message": "Failure at user get service."
                }
            
            renterEmailAddress = user_get_renter['data']['emailAddress']
            print(renterEmailAddress)

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

            # start email amqp
            result = {
                'renterEmailAddress': renterEmailAddress,
                'ownerEmailAddress': ownerEmailAddress,
                'scenario': "return"
            }
            email_amqp = email(result)

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
    redirect_url = payment_result['session']['url']

    if code not in range(200, 300):
        # Inform the error microservice
        print('\n\n-----Publishing the (payment error) message with routing_key=payment.error-----')

        errorHandling(payment_result, code, current_service)
        
        return {
        "code": code,
        "data": payment_result,
    }
    else:
        return {
            "code": code,
            "redirect_url": redirect_url
        }   
        # return payment_result

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
        print('\n\n-----Publishing the (payment error) message with routing_key=payment.error-----')

        errorHandling(payment_result, code, current_service)

        return {
        "code": code,
        "data": payment_result,
    }
    else:
        return payment_result

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
        return {
            "code": code,
            "data": rental_service_result
        }
    else:
        return rental_service_result
    
# function for getting whole rental list
def listRental(sendData):

    # invoking rental microservice
    current_service = "rental"
    print('\n\n-----Invoking get rental microservice-----')   
    
    rental_service_result = invoke_http(
        rental_list_URL, method="POST", json=sendData)
    
    print("rental_status_result:", rental_service_result, '\n')

    # error handling for rental microservice
    code = rental_service_result["code"]
    if code not in range(200, 300):
        #send to error amqp and return stuff here
        errorHandling(rental_service_result, code, current_service)
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

# function for get all user service
def getAllUsers():
    # invoking user microservice
    current_service = "user"

    print('\n\n-----Invoking user microservice-----')   
    
    user_service_result = invoke_http(
        user_get_URL, method="GET", json={})
    
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

# function for user service
def getUser(owner_id):
    # invoking user microservice
    current_service = "user"

    print('\n\n-----Invoking user microservice-----')   
    user_URL = user_get_URL + f"/{owner_id}" 
    
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
    
# function for email
def email(result):
    # invoking amqp for email
    print('\n\n-----Invoking email microservice-----')  
    
    message = json.dumps(result)
    owner = result['ownerEmailAddress']
    renter = result['renterEmailAddress']
    scenario = result['scenario']
    print(f"\nOwner: {owner}\nRenter: {renter}\nScenario: {scenario} ")  

    channel.basic_publish(exchange=exchangename, routing_key="email", body=message, properties=pika.BasicProperties(delivery_mode = 2))


if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for master microservice")
    app.run(host="0.0.0.0", port=PORT, debug=True)
