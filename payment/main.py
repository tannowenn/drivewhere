# This example sets up an endpoint using the Flask framework.
# Watch this video to get started: https://youtu.be/7Ul1vfmsDck.
import os
from dotenv import load_dotenv
import stripe

from flask import Flask, redirect, request

# Load stripe test API key
load_dotenv()
stripe.api_key = os.getenv('STRIPE_KEY')

app = Flask(__name__)

@app.route('/payment/success')
def success():
    return "PAYMENT SUCCESS"

@app.route('/payment/cancel')
def cancel():
    return "PAYMENT CANCELLED"

# Use curl -X POST -is "http://localhost:4242/payment/rent" -d "" to test
# Use card number 4000003720000278 to ensure balance goes directly to stripe account
# Note that payment fees are 3.9% + $0.50 for the card above.
@app.route('/payment/rent', methods=['POST'])
def rent_car():
    body = request.get_json()
    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': 'sgd',
                'product_data': {
                    'name': body['rentalId'],
                },
                'unit_amount': body['paymentAmt'],
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:4242/payment/success',
        cancel_url='http://localhost:4242/payment/cancel',
    )

    return redirect(session.url, code=303)

@app.route('/payment/return', methods=['POST'])
def return_car():
    body = request.get_json()
    transfer = stripe.Transfer.create(
        amount=body['paymentAmt'],
        currency="sgd",
        destination="acct_1OuWDc2MktsaBBhJ",
    )

    return {
        'code': 201,
        'data': transfer
    }

if __name__== '__main__':
    app.run(port=4242, debug=True)
