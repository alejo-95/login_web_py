from flask import Flask
from flask import render_template, redirect, request, Response, session, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__,template_folder='templete')


app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Alejodev1995'
app.config['MYSQL_DB']='prueba'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/acceso-login', methods=["GET","POST"])
def login():
    
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']
        
        
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM USUARIOS WHERE name = %s AND password = %s',(_correo, _password,))
        account = cur.fetchone()
        
        if account:
            session['logueado'] = True
            session['id']= account['id']
            
            return render_template('admin.html')
        
        else:
            return render_template('index.html')
        
    


if __name__ == '__main__':
    app.secret_key="projectoU"
    app.run(debug=True,host='0.0.0.0', port=5000, threaded=True)