from package import db
from werkzeug.security import generate_password_hash, check_password_hash

class Customer(db.Model):
    __tablename__ = 'customer'
    cust_id = db.Column('cust_id',db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.Text)
    phone = db.Column(db.String(100))
    
    invoices = db.relationship('Invoice',backref='invoice')
    
    def __init__ (self,name,address,phone):
        self.name = name
        self.address = address
        self.phone = phone


class Invoice(db.Model):
    __tablename__ = 'invoice'
    inv_id = db.Column('inv_id',db.Integer, primary_key=True)
    cust_id =  db.Column(db.Integer, db.ForeignKey('customer.cust_id'))
    date = db.Column(db.DateTime)
    amount = db.Column(db.Float)
    remark = db.Column(db.Text)
    status = db.Column(db.Boolean)
    
    def __init__ (self,cust_id,date,amount,remark,status):
        self.cust_id = cust_id
        self.date = date
        self.amount = amount 
        self.remark = remark
        self.status = status


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column('user_id',db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))

    def __init__ (self,username,password,role):
        self.username = username
        self.password_hash = self.set_password(password)
        self.role = role
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)