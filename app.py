from flask import Flask
from flask import render_template, redirect, request, Response, session, url_for, flash
from flask_mysqldb import MySQL


app = Flask(__name__,template_folder='templete')
mysql = MySQL()

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Alejodev1995'
app.config['MYSQL_DB']='prueba'
app.config['MYSQL_CURSORCLASS']='DictCursor'
#mysql=MySQL(app)
mysql.init_app(app)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('menu/admin.html')

# Metodos para registro e ingreso
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
                return render_template('menu/admin.html')
        
        else:
            return render_template('index.html',mensaje='El usuario y/o la contraseña son incorrectos')
        
    

@app.route('/registro')
def registro():
    return render_template('Login_register/registro.html')


@app.route('/create-registro', methods=["GET","POST"])
def createRegister():
    correo= request.form['txtCorreo']
    password= request.form['txtPassword']
    
    if correo == '':
        return render_template('Login_register/registro.html', registerWrong='Por favor ingrese un usuario valido')
    elif password == '':
        return render_template('Login_register/registro.html', registerWrong='Por favor ingrese un usuario valido')
    else:
        cur = mysql.connection.cursor()
        cur.execute("Insert into usuarios(name,password, idperfil) values(%s,%s,'2')",(correo, password))
        mysql.connection.commit()
        return render_template('index.html',mensajeRegister ='El usuario ha sido registrado con exito')
    
#Metodos para usuario
#listar
@app.route('/listar-usuarios')
def ListUser():
    cur=mysql.connection.cursor()

    cur.execute('SELECT * FROM usuarios')
    data = cur.fetchall()

    cur.close()
    return render_template('Users/list_user.html', users = data)
#editar
@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_user(id):
    cur=mysql.connection.cursor()
    
    cur.execute('SELECT * FROM usuarios WHERE id = %s', (id,))
    data = cur.fetchall()
    cur.close()
    #print(data[0])
    return render_template('Users/edit_user.html', users = data[0])
#actualizar
@app.route('/update/<id>', methods=['POST'])
def update_employee(id):
    if request.method == 'POST':
        name = request.form['txtCorreo']
        password = request.form['txtPassword']
        
        if name == '':
            return render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        elif password == '':
            return render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE usuarios
                SET name = %s,
                    password = %s
                WHERE id = %s
            """, (name, password,  id))
        flash('Employee Updated Successfully')
        mysql.connection.commit()
        return redirect(url_for('ListUser'))
#Eliminar 
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_employee(id):
#agregar  
    cur=mysql.connection.cursor()
    
    cur.execute('DELETE FROM usuarios WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Employee Removed Successfully')
    return redirect(url_for('ListUser'))
#renderizar
@app.route('/user')
def user():
    return render_template('Users/create_user.html')
#agregar
@app.route('/add-user', methods=["POST","GET"])
def addUser():
    correo = request.form['txtCorreo']
    password = request.form['txtPassword']
    
    if correo == '':
        return render_template('Users/create_user.html', registerWrong='Por favor ingrese un usuario valido')
    elif password == '':
        return render_template('Users/create_user.html', registerWrong='Por favor ingrese un usuario valido')
    # if not correo or not password:
    #     return render_template('Users/create_user.html', registerWrong='Por favor ingrese un usuario válido')
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (name, password, idperfil) VALUES (%s, %s, '2')", (correo, password))
            mysql.connection.commit()
            return render_template('Users/create_user.html', mensajeRegister='El usuario ha sido registrado con éxito')
        except Exception as e:
            # Manejar la excepción (por ejemplo, mostrar un mensaje de error o registrar el error en un archivo de registro)
            return render_template('Users/create_user.html', registerWrong='Error al registrar el usuario')



if __name__ == '__main__':
    app.secret_key="projectoU"
    app.run(debug=True,host='0.0.0.0', port=3000, threaded=True)