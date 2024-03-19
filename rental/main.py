from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import googlemaps
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/rental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Rental(db.Model):
    __tablename__ = 'rental'

    rentalId = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(16),nullable=False)
    userId = db.Column(db.Integer,nullable=False)
    address = db.Column(db.String(255),nullable=False)
    carModel = db.Column(db.String(255),nullable=False)
    carMake = db.Column(db.String(255),nullable=False)
    capacity = db.Column(db.Integer,nullable=False)
    carPlate = db.Column(db.String(16),nullable=False)




    def json(self):
        return {"rentalId": self.rentalId, "status": self.status, "userId": self.userId, "address": self.address, "carModel" : self.carModel, "carMake" : self.carMake, "capacity" : self.capacity, "carPlate" : self.carPlate}


@app.route("/rental")
def get_open_rental_listings():
    rental_list = db.session.scalars(db.select(Rental).filter_by(status="open")).all()
    data = request.get_json()
    if len(rental_list):
        rental_dict = []
        for listing in rental_list:
            listing = listing.json()
            gmaps = googlemaps.Client(key='AIzaSyBkH3BTvWeG9UzLMNhSJsm95KxNNDpi0yE')
            source = data['address']
            destination = listing['address']
            direction_result = gmaps.directions(source,destination)
            listing['distance'] = direction_result[0]['legs'][0]['distance']['text']
            rental_dict.append(listing)
        return jsonify(
            {
                "code": 200,
                "data": {
                    "rental_list": [listing for listing in rental_dict]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no listings."
        }
    ), 404

@app.route("/rental/info")
def get_rental_info():
    data = request.get_json()
    rentId = data["rentalId"]
    rental_list = db.session.scalars(db.select(Rental).filter_by(rentalId = rentId).limit(1)).first()
    if rental_list:
        userId = rental_list.userId
        return jsonify(
            {
                "code": 200,
                "data": {
                    "userId": userId
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no listings."
        }
    ), 404

@app.route("/rental/create", methods=['POST'])
def create_rental_listing():
    data = request.get_json()
    listing = Rental(**data)

    try:
        db.session.add(listing)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred creating the listing."
            }
        ), 500


    return jsonify(        
        {
            "code": 201,
            "data": listing.json()
        }
    ), 201

@app.route("/rental/update", methods=['PUT'])
def update_rental_status():
    data = request.get_json()
    rentId = data["rentalId"]
    rental_listing = db.session.scalars(db.select(Rental).filter_by(rentalId=rentId).limit(1)).first()
    if rental_listing:
        rental_listing.status = data["status"]
        db.session.commit()
        return jsonify(        
        {
            "code": 201,
            "data": rental_listing.json()
        }
        ), 201

    return jsonify(
        {
            "code": 404,
            "message": "Error in updating"
        }
        ), 404
    

if __name__== '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)