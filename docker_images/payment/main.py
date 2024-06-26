import stripe
import math
import requests

from os import environ
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta

# Define the target timezone
target_timezone = timezone(timedelta(hours=8))

# Load stripe test API key
stripe.api_key = environ.get('STRIPE_KEY')

# Global variables
COMMISSION_PCT = 0.1
PAYMENT_FEE_PCT = 0.039
PAYMENT_FEE_FLAT = 0.5
PORT = environ.get('PORT') or 5004
MASTER_HOST = environ.get('MASTER_HOST') or "localhost"
MASTER_PORT = environ.get('MASTER_PORT') or 5100
if MASTER_HOST == "master":
    MASTER_HOST = "localhost"

app = Flask(__name__)
CORS(app)
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
    created = db.Column(db.DateTime, nullable=False, default=datetime.now().astimezone(target_timezone))
    modified = db.Column(db.DateTime, nullable=False,
                         default=datetime.now().astimezone(target_timezone), onupdate=datetime.now().astimezone(target_timezone))

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
                "code": 201
            }
        )

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while processing payment. " + str(e)
            }
        )

@app.route('/payment/rent', methods=['POST'])
def rent_car():
    try:
        body = request.get_json()
        payment_amount = int(float(body['paymentAmt'])*100)

        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'sgd',
                    'product_data': {
                        'name': f"Rental {body['rentalId']}",
                    },
                    'unit_amount': payment_amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"http://{MASTER_HOST}:{MASTER_PORT}/master/rental/continue?rental_id={body['rentalId']}&payer_id={body['payerId']}&payee_id={body['payeeId']}&renter_email_address={body['renterEmailAddress']}&owner_email_address={body['ownerEmailAddress']}"+'&session_id={CHECKOUT_SESSION_ID}',
            cancel_url=f'http://{MASTER_HOST}:{MASTER_PORT}/master/rental/cancel',
        )

        return jsonify(
            {
                "code": 200,
                "session": session
            }
        ), 200
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while proceeding to payment. " + str(e)
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
        release_amt = (release_amt * (1-PAYMENT_FEE_PCT) - PAYMENT_FEE_FLAT) * (1-COMMISSION_PCT)
        release_amt = math.floor(release_amt * 100)
        
        stripe.Transfer.create(
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
    app.run(host="0.0.0.0", port=PORT, debug=True)
