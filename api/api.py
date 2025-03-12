from flask import Flask, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'mysql'
app.config['MYSQL_USER'] = 'pila'
app.config['MYSQL_PASSWORD'] = 'pila'
app.config['MYSQL_DB'] = 'pila'
mysql = MySQL(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/locations', methods=['GET'])
def locations():
    cur = mysql.connection.cursor()
    cur.execute('''
        select UNIX_TIMESTAMP(l.date) as date, l.id, l.type, l.lat, l.lng
        from locations l, (select max(date) as d, id FROM locations where lat > 0 and lng > 0 group by id) lg 
        where lg.id = l.id and lg.d = l.date
    ''')
    data = cur.fetchall()
    cur.close()
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True)
    