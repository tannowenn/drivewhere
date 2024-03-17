from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/book'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Rental(db.Model):
    __tablename__ = 'rental'

    rentalId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(16),nullable=False)
    userId = db.Column(db.Integer,nullable=False)
    address = db.Column(db.String(255,nullable=False))
    carModel = db.Column(db.String(255),nullable=False)
    carMake = db.Column(db.String(255),nullable=False)
    capacity = db.Column(db.Integer,nullable=False)
    carPlate = db.Column(db.String(16),nullable=False)


    def __init__(self, rentalId, status, userId, address, carModel, carMake, capacity, carPlate):
        self.rentalId = rentalId
        self.status = status
        self.userId = userId
        self.address = address
        self.carModel = carModel
        self.carMake = carMake
        self.capacity = capacity
        self.carPlate = carPlate


    def json(self):
        return {"rentalId": self.rentalId, "status": self.status, "userId": self.userId, "lat": self.lat, "ln" : self.ln, "carModel" : self.carModel, "carMake" : self.carMake, "capacity" : self.capacity, "carPlate" : self.carPlate}


@app.route("/rental")
def get_open_rental_listings():
    rental_list = db.session.scalars(db.select(Rental).filter_by(status="open")).all()

    if len(rental_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "rental_list": [listing.json() for listing in rental_list]
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
def get_open_rental_listings():
    data = request.get_json()
    rentId = data["rentalId"]
    rental_list = db.session.scalars(db.select(Rental).filter_by(rentalId=rentId)).limit(1)

    if len(rental_list):
        userId = rental_list['userId']
        return jsonify(
            {
                "code": 200,
                "data": {
                    "userId": userId.json()
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
    rental_listing = db.session.scalars(db.select(Rental).filter_by(rentalId=rentId)).limit(1)
    if len(rental_listing):
        rental_listing["status"] = data["status"]
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
    app.run(host="0.0.0.0", port=5000, debug=True)