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
        if 'Access-Token' in request.headers:
            token = request.headers['Access-Token']
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(jwt=token, key=app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query \
                .filter_by(public_id=data['public_id']) \
                .first()
            current_user.last_req = datetime.now()
            db.session.commit()
        except Exception:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        return f(current_user, *args, **kwargs)

    return decorated


# create post
@app.route('/create_post', methods=['POST'])
@token_required
def create_post(current_user):
    post = request.json
    if not post or not post.get('text'):
        # returns 401 if any email or / and password is missing
        return jsonify({'Message': 'Text require'}), 401

    title, text, author_id = post.get('title'), post.get('text'), current_user.id
    post = Post(
        title=title,
        text=text,
        author_id=author_id,
    )
    db.session.add(post)
    db.session.commit()

    return jsonify({'Message': 'Successfully posted'}), 201


@app.route('/post_rate/id=<post_id>/rate=<post_rate>')
@token_required
def post_rate(current_user, post_id, post_rate):
    if not post_rate.isdigit() or not post_id.isdigit():
        return jsonify({'Message': 'Please rate post 1(Like) or 0(Dislike), or enter valid post id'}), 400
    post_rate = bool(int(post_rate))
    rate = Like.query \
        .filter_by(post_id=post_id, user_id=current_user.id) \
        .first()
    if not rate:
        like = Like(
            post_id=post_id,
            user_id=current_user.id,
            rate=post_rate,
        )
        db.session.add(like)
        db.session.commit()
        return jsonify({'Message': 'Successfully rated.'}), 201
    if post_rate != rate.rate:
        rate.rate = post_rate
        db.session.commit()
    return jsonify({'Message': 'Successfully rated.'}), 201


# route for logging user in
@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({'Message': 'Could not verify'}), 401

    user = User.query \
        .filter_by(email=auth.get('email')) \
        .first()

    if not user:
        # returns 401 if user does not exist
        return jsonify({'Message': 'User does not exist !!!'}), 401

    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])
        user.last_login = datetime.now()
        db.session.commit()
        return jsonify({'Access-Token': token}), 201
    # returns 403 if password is wrong
    return jsonify({'Message': 'Wrong Password !!'}), 403


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name, email = data.get('name'), data.get('email')
    password = data.get('password')
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
        return jsonify({'Message': 'Successfully registered.'}), 201
    else:
        # returns 202 if user already exists
        return jsonify({'Message': 'User already exists. Please Log in.'}), 202


# need to encode symbols for curl request
# urllib.parse.quote('/api/analistics/?date_from=2022-08-10&date_to=2022-08-30')
@app.route('/api/analistics/?date_from=<date_from>&date_to=<date_to>/')
def get_analystic(date_from, date_to):
    try:
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Please enter valid date %Y-%m-%d'}), 400
    analystic = Like.query \
        .filter(date_from < Like.date) \
        .filter(date_to > Like.date)

    result = {}
    for i in analystic:
        if i.date.strftime('%Y-%m-%d') not in result:
            result[i.date.strftime('%Y-%m-%d')] = [f"{i}"]
        else:
            result[i.date.strftime('%Y-%m-%d')].append(f"{i}")
    return jsonify(result), 201


@app.route('/user_activity')
@token_required
def get_data(current_user):
    last_login = current_user.last_login
    last_req = current_user.last_req
    return jsonify({'Last request': last_req, 'Last login': last_login})
