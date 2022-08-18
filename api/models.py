from api import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))
    last_login = db.Column(db.DateTime(timezone=True))
    last_req = db.Column(db.DateTime(timezone=True))
    likes = db.relationship('Like', backref='user')
    posts = db.relationship('Post', backref='user')

    def __repr__(self):
        return f"<User name: {self.name}, email: {self.email}, posts {len(self.posts)}, likes{len(self.likes)}>"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    text = db.Column(db.String(1000))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    likes = db.relationship('Like', backref='post')

    def __repr__(self):
        return f"<Author id: {self.author_id}, title: {self.title}, text {self.text}>"


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    rate = db.Column(db.Boolean)

    def __repr__(self):
        return f"Date: {self.date}, rate: {self.rate}, user_id {self.user_id}, post_id {self.post_id}"
