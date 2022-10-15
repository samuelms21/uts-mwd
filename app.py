from package import app, db
from package.models import Customer, Invoice, User

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Customer': Customer, 'Invoice': Invoice}