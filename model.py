from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class User(db.Model):
    """Information for users"""

    __tablename__ = 'users'

    user_table_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(75), nullable=False)


    def __repr__(self):
        """Provide helpful information when printed to the console"""

        return "<user_table_id: %s, user_id: %s"\
            % (self.user_table_id, self.user_id)

class Search(db.Model):
    """Information for searches"""

    __tablename__ = 'searches'

    search_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(75), db.ForeignKey("users.user_id"))
    # search_term = I HAVE A VARYING NUMBER OF SEARCH TERMS...

class UserSearch(db.Model)
# search table based around search terms
# association table user search id, user search id, user id search id

# make a feed to show common searches



class Trip(db.Model):
    """Search history of the user."""

    __tablename__ = "trips"

    trip_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(75), db.ForeignKey("users.user_id"))
    origin = db.Column(db.String(200))
    start_lat = db.Column(db.Float)
    start_lng = db.Column(db.Float)
    destination = db.Column(db.String(200))
    end_lat = db.Column(db.Float)
    end_lng = db.Column(db.Float)
    mileage = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow())

    user = db.relationship('User', backref=db.backref('trips'))


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<user_id = %s origin = %s destination = %s mileage = %s date = %s>" % (
            self.user_id, self.origin, self.destination, self.mileage, self.date)

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///muse'
    db.app = app
    db.init_app(app)

    db.create_all()

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB"
