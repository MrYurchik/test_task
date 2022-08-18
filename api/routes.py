import pdb
import uuid
from datetime import datetime, timedelta
from functools import wraps


# decorator for verifying the JWT
import jwt
from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from api import app, db
from api.models import User, Post, Like


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'X-Access-Token' in request.headers:
            token = request.headers['X-Access-Token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            print('try decode')
            data = jwt.decode(jwt=token, key=app.config['SECRET_KEY'], algorithms=['HS256'])
            print(data)
            current_user = User.query \
                .filter_by(public_id=data['public_id']) \
                .first()
        except Exception as e:
            print(e)
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated


# User Database Route
# this route sends back list of users
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    users = User.query.all()
    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        # appending the user data json
        # to the response list
        output.append({
            'public_id': user.public_id,
            'name': user.name,
            'email': user.email
        })

    return jsonify({'users': output})



# create post
@app.route('/create_post', methods=['POST'])
@token_required
def create_post(current_user):
    # creates dictionary of form data
    post = request.json
    if not post or not post.get('text'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Write some post..',
            401,
            {'WWW-Authenticate': 'Basic realm ="Text require"'}
        )

    title = post.get('title')
    text = post.get('text')
    author_id = current_user.id
    # database ORM object
    post = Post(
        title=title,
        text=text,
        author_id=author_id,
    )
    # insert user
    db.session.add(post)
    db.session.commit()

    return make_response('Successfully posted.', 201)


@app.route('/post_rate/<post_id>/<post_rate>')
@token_required
def post_rate(current_user, post_id, post_rate):
    like = Like(
        post_id=post_id,
        user_id=current_user.id,
        rate=post_rate,
    )
    # insert user
    db.session.add(like)
    db.session.commit()
    ##############need to add block where to check if like exist and update if exist!!!!


    return make_response('Successfully posted.', 201)

# route for logging user in
@app.route('/login', methods=['POST'])
def login():
    # creates dictionary of form data
    auth = request.json
    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    user = User.query \
        .filter_by(email=auth.get('email')) \
        .first()

    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])
        return make_response(jsonify({'token': token}), 201)
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )


# signup route
@app.route('/signup', methods=['POST'])
def signup():
    # creates a dictionary of the form data
    data = request.json

    # gets name, email and password
    name, email = data.get('name'), data.get('email')
    password = data.get('password')
    print(f'PASSWORD {password}')
    print(f'PASSWORD {name}')
    print(data)


    # checking for existing user
    user = User.query \
        .filter_by(email=email) \
        .first()
    if not user:
        # database ORM object
        user = User(
            public_id=str(uuid.uuid4()),
            name=name,
            email=email,
            password=generate_password_hash(password)
        )
        # insert user
        db.session.add(user)
        db.session.commit()

        return make_response('Successfully registered.', 201)
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)
