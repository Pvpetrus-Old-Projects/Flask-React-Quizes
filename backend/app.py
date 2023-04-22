from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)
ma = Marshmallow(app)


@app.before_first_request
def create_tables():
    db.create_all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    email = db.Column(db.String(50))

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password', 'email')


userSchema = UserSchema()
usersSchema = UserSchema(many=True)


@app.route('/add', methods=['POST'])
def add_user():
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']

    user = User(username=username, password=password, email=email)
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return f"Could not add a user. Error message: {e}"
    return userSchema.jsonify(user)


@app.route('/get/<username>/<password>', methods=['GET'])
def get_user(username, password):
    user = User.query.filter_by(username=username, password=password).first()
    if user is None:
        return "This user does not exist"
    return userSchema.jsonify(user)


@app.route('/get/<id>', methods=['GET'])
def get_user_by_id(id):
    user = User.query.get(id)
    if user is None:
        return "This user does not exist"
    return userSchema.jsonify(user)


@app.route('/get', methods=['GET'])
def get_all_users():
    """if users is None:
            return "No users in database"
        usersJson = []
        for user in users:
            usersJson.append({"username":user.username,"password":user.password,"email":user.email})
        return usersJson"""
    users = User.query.all()
    users = usersSchema.dump(users)
    return jsonify(users)

@app.route('/update/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)

    username = request.json['username']
    password = request.json['password']
    email = request.json['email']

    user.username = username
    user.password = password
    user.email = email
    db.session.commit()
    if user is None:
        return "User with this id does not exist"
    return userSchema.jsonify(user)

@app.route('/delete/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user is None:
        return "This user does not exist"
    db.session.delete(user)
    db.session.commit()
    return userSchema.jsonify(user)