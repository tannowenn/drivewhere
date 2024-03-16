# This example sets up an endpoint using the Flask framework.
# Watch this video to get started: https://youtu.be/7Ul1vfmsDck.
import os
from dotenv import load_dotenv
import stripe

from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime

# Load stripe test API key
load_dotenv()
stripe.api_key = os.getenv('STRIPE_KEY')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Payment(db.Model):
    __tablename__ = 'payment'

    paymentId = db.Column(db.Integer, primary_key=True)
    rentalId = db.Column(db.String(32), nullable=False)
    payerId = db.Column(db.String(32), nullable=False)
    payeeId = db.Column(db.String(32), nullable=False)
    amountSgd = db.Column(db.Float(precision=2), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified = db.Column(db.DateTime, nullable=False,
                         default=datetime.now, onupdate=datetime.now)

    def __init__(self, paymentId, rentalId, payerId, payeeId, amountSgd, status, created, modified):
        self.paymentId = paymentId
        self.rentalId = rentalId
        self.payerId = payerId
        self.payeeId = payeeId
        self.amountSgd = amountSgd
        self.status = status
        self.created = created
        self.modified = modified

    def json(self):
        return {"paymentId": self.paymentId, "rentalId": self.rentalId, "payerId": self.payerId, "payeeId": self.payeeId, "amountSgd": self.amountSgd, "status": self.status, "created": self.created, "modified": self.modified}

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
