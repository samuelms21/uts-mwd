from package import app, db
from flask import render_template, redirect, request, url_for, session
from package.models import User, Invoice, Customer
from sqlalchemy import update

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
    # if session.get("username"):
    #     return redirect(url_for('index'))

    title = 'Login'

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # If username or password is empty
        if not (username and password):
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

    return render_template('login.html', title=title)


@app.route('/logout')
def logout():
    session["username"] = None
    return redirect(url_for('login'))


@app.route('/add_invoice', methods=['GET', 'POST'])
def add_invoice():
    if request.method == 'POST':
        cust_id = request.form.get('cust_id')
        date = request.form.get('date')
        amount = request.form.get('amount')
        remark = request.form.get('remark')
        
        print('Customer ID:', cust_id)
        print('Date:', date)
        print('Date data type:', type(date))
        print('Amount:', amount)
        print('Remark:', remark)

        # Check if cust_id exists
        if Customer.query.filter_by(cust_id=cust_id).first():
            # User exists, proceed to add invoice to database
            new_invoice = Invoice(cust_id, date, amount, remark, status=False)
            db.session.add(new_invoice)
            db.session.commit()
            return redirect(url_for('sales', message='New invoice added to database.'))

        # cust_id does not exist in db
        return redirect(url_for('sales', message='Customer does not exist.'))
        
@app.route('/finance')
def finance():
    title = 'Finance'

    if not (session.get('username') and session.get("role") == 'finance'):
        return redirect(url_for('login'))

    return render_template('finance.html', title=title)


@app.route('/approve_payment',methods=['POST'])
def approve_payment():
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
        
    title = 'Finance'

    if request.method == 'POST':
        data = request.form

        inv_ids = [int(i) for i in data.keys()]

        for inv_id in inv_ids:
            invoice = db.session.query(Invoice).filter(Invoice.inv_id==inv_id).first()
            invoice.status = True
        
        db.session.commit()

        all_invoice = Invoice.query.all()

        invoices = []    

        for inv in all_invoice:
            if inv.status == False:
                invoices.append(inv)
            inv.date = str(inv.date)
            inv.date = inv.date[:inv.date.index(' ')]
            inv.date = change_date_format(inv.date)
        return render_template('finance.html', title=title, invoices=invoices)