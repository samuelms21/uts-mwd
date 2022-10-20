from package import app, db
from flask import render_template, redirect, request, url_for, session, flash
from package.models import User, Invoice, Customer
import string

@app.route('/')
def index():
    if not session.get('username'):
        return redirect(url_for('login'))
    else:
        # Username and role must exist already in session data
        # Therefore, they have logged in
        # Redirect them to their respective role page
        return redirect(url_for(session['role']))
    
    
@app.route('/sales')
def sales():
    title = 'Sales'
    if not (session.get('username') and session.get("role") == 'sales'):
        return redirect(url_for('login'))
    return render_template('sales.html', title=title, message=None)


@app.route('/login', methods=['POST', 'GET'])
def login():
    title = 'Login'

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # If username or password is empty
        if not (username and password):
            flash('Username or Password is Empty!')
            return render_template('login.html')
        
        # If username and password is not empty (proceed)
        user_is_found = User.query.filter_by(username=username).first()

        # If user exists in database
        if user_is_found:
            pass_is_valid = user_is_found.check_password(password)

            if pass_is_valid:
                session['username'] = username
                session['role'] = user_is_found.role

                return redirect(url_for(session['role']))
            else:
                flash('Wrong password', 'error')
                return render_template('login.html', title=title)
                
        else:
            flash('Username not found', 'error')
            return render_template('login.html', title=title)

    return render_template('login.html', title=title)

@app.route('/logout')
def logout():
    session["username"] = None
    session["role"] = None
    return redirect(url_for('login'))

@app.route('/add_invoice', methods=['GET', 'POST'])
def add_invoice():
    if request.method == 'POST':
        cust_id = request.form.get('cust_id')
        date = request.form.get('date')
        amount = request.form.get('amount')
        remark = request.form.get('remark')

        # Check if cust_id exists
        if Customer.query.filter_by(cust_id=cust_id).first():
            # User exists, proceed to add invoice to database
            new_invoice = Invoice(cust_id, date, amount, remark, status=False)
            db.session.add(new_invoice)
            db.session.commit()
            flash('Invoice succesfully added!', 'success')
            return redirect(url_for('sales'))
        else:
            # cust_id does not exist in db
            flash('Customer not found.', 'error')
            return redirect(url_for('sales'))
        
        return redirect(url_for('sales'))
        
def change_date_format(date:str):
    months_in_year = ['','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    date = date.split('-')
    date = date[::-1]
    bulan = months_in_year[int(date[1])]
    newDate = ""
    newDate+=date[0]
    newDate+='-'
    newDate+=bulan
    newDate+='-'
    newDate+=date[-1]
    return newDate

@app.route('/finance')
def finance():
    title = 'Finance'

    if not (session.get('username') and session.get("role") == 'finance'):
        return redirect(url_for('login'))
    all_invoice = Invoice.query.all()

    invoices = []    

    for inv in all_invoice:
        if inv.status == False:
            invoices.append(inv)
        inv.date = str(inv.date)
        inv.date = inv.date[:inv.date.index(' ')]
        inv.date = change_date_format(inv.date)
    return render_template('finance.html', title=title,invoices=invoices)

@app.route('/approve_payment',methods=['POST'])
def approve_payment():
    if request.method == 'POST':
        data = request.form

        inv_ids = [int(i) for i in data.keys()]

        for inv_id in inv_ids:
            invoice = db.session.query(Invoice).filter(Invoice.inv_id==inv_id).first()
            invoice.status = True
        
        db.session.commit()

        flash('Invoice(s) payment approved!', 'success')
        return redirect(url_for('finance'))


@app.route('/void_payment',methods=['POST'])
def void_payment():
    if session.get('username') and session.get('role') == 'manager':
        if request.method == 'POST':
            data = request.form

            if not data:
                flash('Select at least one invoice to void.', 'error')
                return redirect(url_for('manager'))

            inv_ids = [int(i) for i in data.keys()]

            for inv_id in inv_ids:
                invoice = db.session.query(Invoice).filter(Invoice.inv_id==inv_id).first()
                invoice.status = False
            
            db.session.commit()
            flash('Void Payment Succesful!', 'success')
            return redirect(url_for('manager'))
    else:
        return redirect(url_for('login'))


@app.route('/manager')
def manager():
    title = 'Manager'

    if not (session.get('username') and session.get("role") == 'manager'):
        return redirect(url_for('login'))
    all_invoice = Invoice.query.all()

    invoices = []    

    total_ar = 0

    for inv in all_invoice:
        if inv.status == True:
            invoices.append(inv)
        else:
            total_ar += inv.amount

        inv.date = str(inv.date)
        inv.date = inv.date[:inv.date.index(' ')]
        inv.date = change_date_format(inv.date)

    return render_template('manager.html', title=title, invoices=invoices, total_ar=total_ar)

@app.route('/manager_cust')
def manager_cust():
    title = 'Manager Cust'

    if not (session.get('username') and session.get("role") == 'manager'):
        return redirect(url_for('login'))
    all_invoice = Invoice.query.all()
    all_cust = Customer.query.all()

    class Cust():
        def __init__ (self,cust_id,name,address,phone,amount=0):
            self.cust_id = cust_id
            self.name = name
            self.address = address
            self.phone = phone
            self.amount = amount

    all_cust_o = []

    for cust in all_cust:
        each_cust = Cust(cust.cust_id,cust.name,cust.address,cust.phone)
        all_cust_o.append(each_cust)

    for inv in all_invoice:
        for cust in all_cust_o:
            if inv.cust_id == cust.cust_id:
                if inv.status == False:
                    cust.amount += inv.amount
                pass
            
    return render_template('manager_cust.html', title=title, all_cust_o=all_cust_o)

@app.route("/update_cust", methods=["POST"])
def update_cust():
    if not (session.get('username') and session.get("role") == 'manager'):
        return redirect(url_for('login'))

    cust_id = request.form.get("cust_id")

    newname = request.form.get("newname")

    newaddress = request.form.get("newaddress")

    newphone = request.form.get("newphone")

    customer = Customer.query.filter_by(cust_id=cust_id).first()
    customer.name = newname
    customer.address = newaddress
    customer.phone = newphone
    db.session.commit()


    return redirect(url_for('manager_cust'))


@app.route("/delete_cust", methods=["POST"])
def delete_cust():
    if not (session.get('username') and session.get("role") == 'manager'):
        return redirect(url_for('login'))

    cust_id = request.form.get("cust_id")
    customer = Customer.query.filter_by(cust_id=cust_id).first()
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for('manager_cust'))

def isValidPhoneNumber(phone_number:str):
    return True if phone_number not in string.ascii_letters and len(phone_number) == 12 else False

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if not (session.get('username') and session.get("role") == 'manager'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        cust_name = request.form.get('cust_name')
        cust_address = request.form.get('cust_add')
        cust_phone = request.form.get('phone_add')
        if isValidPhoneNumber(cust_phone):
            cust = Customer(cust_name,cust_address,cust_phone)
            db.session.add(cust)
            db.session.commit()
        else:
            flash("Gagal, invalid Phone Number!")
            return redirect(url_for('manager_cust'))
        
    return redirect(url_for('manager_cust'))