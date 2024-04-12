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
            session['idperfil'] = account['idperfil']
            
            if session['idperfil'] == 1:
                return render_template("inde.html")
            elif session['idperfil'] == 2:
                return render_template('admin.html')
        
        else:
            return render_template('index.html',mensaje='El usuario y/o la contraseña son incorrectos')
        
    

@app.route('/registro')
def registro():
    return render_template('registro.html')


@app.route('/create-registro', methods=["GET","POST"])
def createRegister():
    correo= request.form['txtCorreo']
    password= request.form['txtPassword']
    

    
    if correo == '':
        return render_template('registro.html', registerWrong='Por favor ingrese un usuario valido')
    elif password == '':
        return render_template('registro.html', registerWrong='Por favor ingrese un usuario valido')
    else:
        cur = mysql.connection.cursor()
        cur.execute("Insert into usuarios(name,password, idperfil) values(%s,%s,'2')",(correo, password))
        mysql.connection.commit()
        
        
        return render_template('index.html',mensajeRegister ='El usuario ha sido registrado con exito')


if __name__ == '__main__':
    app.secret_key="projectoU"
    app.run(debug=True,host='0.0.0.0', port=5000, threaded=True)