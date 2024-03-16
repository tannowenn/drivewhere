from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'


    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    emailAddress = db.Column(db.String(64), nullable=False)
    phoneNum = db.Column(db.String(64))


    def __init__(self, name, emailAddress, phoneNum):
        self.name = name
        self.emailAddress = emailAddress
        self.phoneNum = phoneNum


    def json(self):
        return {"name": self.name, "emailAddress": self.emailAddress, "phoneNum": self.phoneNum}

@app.route("/user")
def get_all():
    userlist = db.session.scalars(db.select(User)).all()
    if len(userlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "users": [user.json() for user in userlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no users."
        }
    ), 404



@app.route("/user/<string:userId>")
def find_by_userId(userId):
    user = db.session.scalars(
    	db.select(User).filter_by(userId=userId).
    	limit(1)
).first()


    if user:
        return jsonify(
            {
                "code": 200,
                "data": user.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404


@app.route("/user", methods=['POST'])
def create_user():
    


    data = request.get_json()
    user = User(**data)


    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred creating the user."
            }
        ), 500


    created_user = user.json()
    created_user["userId"] = user.userId

    return jsonify(
        {
            "code": 201,
            "data": created_user
        }
    ), 201


if __name__ == '__main__':
    app.run(port=5050, debug=True)


