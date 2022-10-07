from bigbeta import db, login_manager
from flask import current_app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
#test comment

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    # LAZY is very important - Notice this is not a column. Since it is a
        # relationship, it will pull all data related to the primary key.
        # In this case, lazy will automatically pull all the posts for the
        # given user.
        # Use this to pull all climb data for a user
        # Note the foreign key set in  Post class
    posts = db.relationship('Post', backref="author", lazy=True)
    sends = db.relationship('Send', backref="author", lazy=True)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')


    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    """
    This is probably comparable to a climb class
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# Looks like this is how you insert data to your database?
#   I think each class is a table
class Send(db.Model):
    """
    Send
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    style = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Send('{self.grade}', '{self.created_at}', '{self.title}')"


class Stocks(db.Model):
    """
    The idea currently is to use this as an object for a table of data.
    The table will be a watchlist, based on morning, 5m, or 1d, containing all
    the data that Jon loves to trade on.
    """

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(8), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    rvol = db.Column(db.Numeric, nullable=False)
    freefloat = db.Column(db.Integer, nullable=False)
    short_interest = db.Column(db.Numeric, nullable=False)
    si_raw = db.Column(db.Integer, nullable=False)
    dtc = db.Column(db.Numeric, nullable=False)
    stories = db.Column(db.Integer, nullable=False)
