from __init__ import db


class User(db.Model):
    unique_num = db.Column(db.String(10), primary_key = True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    email = db.Column(db.String(30))
    id_num = db.Column(db.String(20))
    user_type = db.Column(db.String(5))
    lot_id = db.Column(db.Integer)   
    park_num = db.Column(db.Integer)
    balance = db.Column(db.Float) 

    def __init__(self, unique_num, username, password, email, id_num, user_type,lot_id, park_num, balance):
        self.unique_num = unique_num
        self.username = username
        self.password = password
        self.email = email
        self.id_num = id_num
        self.user_type = user_type
        self.lot_id = lot_id
        self.park_num = park_num
        self.balance = balance

    def __repr__(self):
        return '<User %r>' % self.unique_num


class Park(db.Model):
    num = db.Column(db.Integer)
    lot_id = db.Column(db.Integer)
    park_num = db.Column(db.Integer, primary_key = True)
    park_kind = db.Column(db.String(4))
    park_state = db.Column(db.String(11))
    date_begin = db.Column(db.DateTime)
    date_end = db.Column(db.DateTime)

    def __init__(self, num, lot_id, park_num, park_kind, park_state,date_begin,date_end):
        self.num = num
        self.lot_id = lot_id
        self.park_num = park_num
        self.park_kind = park_kind
        self.park_state = park_state
        self.date_begin = date_begin
        self.date_end = date_end

    def __repr__(self):
        return '<Park %r>' % self.park_num

class Inout(db.Model):
    service_id = db.Column(db.String(20), primary_key = True)
    lot_id = db.Column(db.Integer)
    park_num = db.Column(db.Integer)
    unique_num = db.Column(db.String(10))
    user_type = db.Column(db.String(5))
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)
    park_fee = db.Column(db.Float)

    def __init__(self, service_id, lot_id, park_num, unique_num, user_type, time_in, time_out, park_fee):
        self.service_id = service_id
        self.lot_id = lot_id
        self.park_num = park_num
        self.unique_num = unique_num
        self.user_type =user_type 
        self.time_in = time_in 
        self.time_out = time_out
        self.park_fee = park_fee 

    def __repr__(self):
        return '<Inout %r>' % self.service_id

