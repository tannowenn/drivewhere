# This example sets up an endpoint using the Flask framework.
# Watch this video to get started: https://youtu.be/7Ul1vfmsDck.
import os
from dotenv import load_dotenv
import stripe
import math

from flask import Flask, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Load stripe test API key
load_dotenv()
stripe.api_key = os.getenv('STRIPE_KEY')
PAYMENT_FEE_PCT = 0.039
PAYMENT_FEE_FLAT = 0.5

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('dbURL')
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

    def json(self):
        return {"paymentId": self.paymentId, "rentalId": self.rentalId, "payerId": self.payerId, "payeeId": self.payeeId, "amountSgd": self.amountSgd, "status": self.status, "created": self.created, "modified": self.modified}

@app.route('/')
def root():
    return "WELCOME TO PAYMENT"

@app.route('/payment/success')
def success():
    stripe_session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
    payment_amount = stripe_session['amount_total']
    rental_id = request.args.get('rental_id')
    payer_id = request.args.get('payer_id')
    payee_id = request.args.get('payee_id')
        
    payment = Payment(rentalId=rental_id, payerId=payer_id, payeeId=payee_id, amountSgd=payment_amount/100, status="hold")
    try:
        db.session.add(payment)
        db.session.commit()
        return jsonify(
            {
                "code": 201,
                "data": payment.json()
            }
        ), 201

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while processing payment. " + str(e)
            }
        ), 500

@app.route('/payment/cancel')
def cancel():
    return "PAYMENT CANCELLED"

# Remember to turn off Automatically follow redirects in Postman settings
# Use card number 4000003720000278 to ensure balance goes directly to stripe account
@app.route('/payment/rent', methods=['POST'])
def rent_car():
    try:
        body = request.get_json()
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'sgd',
                    'product_data': {
                        'name': f"Rental {body['rentalId']}",
                    },
                    'unit_amount': body['paymentAmt'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"http://localhost:5000/payment/success?rental_id={body['rentalId']}&payer_id={body['payerId']}&payee_id={body['payeeId']}"+'&session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:5000/payment/cancel',
        )

        return redirect(session.url, code=303)
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while proceeding to checkout. " + str(e)
            }
        ), 500

@app.route('/payment/return', methods=['POST'])
def return_car():
    try:
        body = request.get_json()
        payment = db.session.scalars(
        db.select(Payment).filter_by(rentalId=body['rentalId']).
        limit(1)).first()
        if not payment:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "rentalId": body['rentalId']
                    },
                    "message": "Rental not found."
                }
            ), 404
        elif payment.status == "released":
            return jsonify(
                {
                    "code": 400,
                    "data": {
                        "rentalId": body['rentalId']
                    },
                    "message": "Rental pay has already been released"
                }
            ), 400

        release_amt = payment.amountSgd
        release_amt = release_amt * (1-PAYMENT_FEE_PCT) - PAYMENT_FEE_FLAT
        release_amt = math.floor(release_amt * 100)
        
        transfer = stripe.Transfer.create(
            amount=release_amt,
            currency="sgd",
            destination=body['stripeId'],
        )

        # Update status
        payment.status = "released"
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": payment.json()
            }
        ), 200
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while releasing payment. " + str(e)
            }
        ), 500

if __name__== '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
