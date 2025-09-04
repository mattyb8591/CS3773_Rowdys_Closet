from flask import Flask, redirect, url_for, request
from flaskext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Missi2466$'
app.config['MYSQL_DATABASE_DB'] = 'rc_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT * from products")
data = cursor.fetchone()
print(data)

@app.route('/')
def hello_db():
    return 'Hello World'

'''
@app.route('/success/<name>')
def success(name):
    return 'Welcome, %s' % name

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        return redirect(url_for('success', name=user))
    else:
        user = request.args.get('nm')
        return redirect(url_for('success', name=user))
'''

if __name__ == '__main__':
    app.run(debug=True)

