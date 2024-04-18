from flask import Flask
from flask import render_template, redirect, request, Response, session, url_for, flash
from flask_mysqldb import MySQL
import mysql.connector

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
    
#Metodos para usuario-------------------
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
            return #render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        elif password == '':
            return #render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE usuarios
                SET name = %s,
                    password = %s
                WHERE id = %s
            """, (name, password,  id))
        mysql.connection.commit()
        flash('Usuario actualizado exitosamente')
        return redirect(url_for('ListUser'))
#Eliminar 
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_employee(id):
#agregar  
    cur=mysql.connection.cursor()
    
    cur.execute('DELETE FROM usuarios WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Usuario eliminado exitosamente')
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
        return #render_template('Users/create_user.html', registerWrong='Por favor ingrese un usuario valido')
    elif password == '':
        return #render_template('Users/create_user.html', registerWrong='Por favor ingrese un usuario valido')
    # if not correo or not password:
    #     return render_template('Users/create_user.html', registerWrong='Por favor ingrese un usuario válido')
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (name, password, idperfil) VALUES (%s, %s, '2')", (correo, password))
            mysql.connection.commit()
            flash('Usuario agregado con exito')
            return redirect(url_for('ListUser'))
        except Exception as e:

            return #render_template('Users/create_user.html', registerWrong='Error al registrar el usuario')

#Metodos para perfil
#listar
@app.route('/listar-perfiles')
def ListPerfil():
    cur=mysql.connection.cursor()

    cur.execute('SELECT * FROM perfiles')
    data = cur.fetchall()

    cur.close()
    return render_template('perfil/list_perfil.html', perfil = data)
#Actualizar
@app.route('/updatePerfil/<id>', methods=['POST'])
def updatePerfil(id):
    if request.method == 'POST':
        perfil = request.form['txtPerfil']
        state = request.form['txtEstado']
        
        if perfil == '':
            return #render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        elif state == '':
            return #render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE perfiles
                SET perfiles = %s,
                    estado = %s
                WHERE idperfiles = %s
            """, (perfil, state,  id))
        mysql.connection.commit()
        flash('Perfil actualizado exitosamente')
        return redirect(url_for('ListPerfil'))
#Eliminar
@app.route('/deletePerfil/<string:id>', methods = ['POST','GET'])
def deletePerfil(id): 
    cur=mysql.connection.cursor()
    
    cur.execute('DELETE FROM perfiles WHERE idperfiles = {0}'.format(id))
    mysql.connection.commit()
    flash('Perfil eliminado exitosamente')
    return redirect(url_for('ListPerfil'))
#Agregar
@app.route('/add-perfiles', methods=["POST","GET"])
def addPerfil():
    perfil = request.form['txtPerfil']
    state = request.form['txtEstado']
    
    if perfil == '':
        return 
    elif state == '':
        return 
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO perfiles (perfiles, estado) VALUES (%s, %s)", (perfil, state))
            mysql.connection.commit()
            flash('Perfil agregado con exito')
            return redirect(url_for('ListPerfil'))
        except Exception as e:

            return 

#Metodos para accesorios
#Listar
@app.route('/listar-acce')
def ListAcce():
    cur=mysql.connection.cursor()

    cur.execute('SELECT * FROM accesorios')
    data = cur.fetchall()

    cur.close()
    return render_template('accesorios/list_acce.html', acce = data)
#Actualizar
@app.route('/updateAcce/<id>', methods=['POST'])
def updateAcce(id):
    if request.method == 'POST':
        acce = request.form['txtAcce']
        state = request.form['txtEstado']
        
        if acce == '':
            return #render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        elif state == '':
            return #render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE accesorios
                SET accesorios = %s,
                    estado = %s
                WHERE idaccesorios = %s
            """, (acce, state,  id))
        mysql.connection.commit()
        flash('Accesorio actualizado exitosamente')
        return redirect(url_for('ListAcce'))
#Eliminar
@app.route('/deleteAcce/<string:id>', methods = ['POST','GET'])
def deleteAcce(id): 
    cur=mysql.connection.cursor()
    
    cur.execute('DELETE FROM accesorios WHERE idaccesorios = {0}'.format(id))
    mysql.connection.commit()
    flash('Accesorio eliminado exitosamente')
    return redirect(url_for('ListAcce'))
#Agregar
@app.route('/add-acce', methods=["POST","GET"])
def addAcce():
    acce = request.form['txtAcce']
    state = request.form['txtEstado']
    
    if acce == '':
        return 
    elif state == '':
        return 
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO accesorios (accesorios, estado) VALUES (%s, %s)", (acce, state))
            mysql.connection.commit()
            flash('Accesorio agregado con exito')
            return redirect(url_for('ListAcce'))
        except Exception as e:

            return 


#Metodos para arduinos
#Listar
@app.route('/listar-ard')
def ListArd():
    cur=mysql.connection.cursor()

    cur.execute('SELECT * FROM arduinos')
    data = cur.fetchall()

    cur.close()
    return render_template('arduinos/list_arduino.html', ard = data)
#Actualizar
@app.route('/updateArd/<id>', methods=['POST'])
def updateArd(id):
    if request.method == 'POST':
        ard = request.form['txtArd']
        state = request.form['txtEstado']
        
        if ard == '':
            return #render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        elif state == '':
            return #render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE arduinos
                SET arduino = %s,
                    estado = %s
                WHERE idarduinos= %s
            """, (ard, state,  id))
        mysql.connection.commit()
        flash('Arduino actualizado exitosamente')
        return redirect(url_for('ListArd'))
#Eliminar
@app.route('/deleteArd/<string:id>', methods = ['POST','GET'])
def deleteArd(id): 
    cur=mysql.connection.cursor()
    
    cur.execute('DELETE FROM arduinos WHERE idarduinos = {0}'.format(id))
    mysql.connection.commit()
    flash('Arduino eliminado exitosamente')
    return redirect(url_for('ListArd'))
#Agregar
@app.route('/add-ard', methods=["POST","GET"])
def addArd():
    ard = request.form['txtArd']
    state = request.form['txtEstado']
    
    if ard == '':
        return 
    elif state == '':
        return 
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO arduinos (arduino, estado) VALUES (%s, %s)", (ard, state))
            mysql.connection.commit()
            flash('Arduino agregado con exito')
            return redirect(url_for('ListArd'))
        except Exception as e:

            return 


#Metodos para tipo_cliente
#Listar
@app.route('/listar-tipClient')
def ListTipClient():
    cur=mysql.connection.cursor()

    cur.execute('SELECT * FROM tipo_clientes')
    data = cur.fetchall()

    cur.close()
    return render_template('tipo_cliente/list_tipo_cliente.html', tip = data)
#Actualizar
@app.route('/updateTipClient/<id>', methods=['POST'])
def updateTipClient(id):
    if request.method == 'POST':
        tip = request.form['txtTip']
        state = request.form['txtEstado']
        
        if tip == '':
            return #render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        elif state == '':
            return #render_template('Users/edit_user.html', registerWrong='Por favor ingrese un usuario valido')
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE tipo_clientes
                SET tipo = %s,
                    estado = %s
                WHERE idtipo_clientes= %s
            """, (tip, state,  id))
        mysql.connection.commit()
        flash('Tipo cliente actualizado exitosamente')
        return redirect(url_for('ListTipClient'))
#Eliminar
@app.route('/deleteTipClient/<string:id>', methods = ['POST','GET'])
def deleteTipClient(id): 
    cur=mysql.connection.cursor()
    
    cur.execute('DELETE FROM tipo_clientes WHERE idtipo_clientes = {0}'.format(id))
    mysql.connection.commit()
    flash('Tipo cliente eliminado exitosamente')
    return redirect(url_for('ListTipClient'))
#Agregar
@app.route('/add-tip', methods=["POST","GET"])
def addTipClient():
    tip = request.form['txtTip']
    state = request.form['txtEstado']
    
    if tip == '':
        return 
    elif state == '':
        return 
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tipo_clientes (tipo, estado) VALUES (%s, %s)", (tip, state))
            mysql.connection.commit()
            flash('Tipo cliente agregado con exito')
            return redirect(url_for('ListTipClient'))
        except Exception as e:

            return 







if __name__ == '__main__':
    app.secret_key="projectoU"
    app.run(debug=True,host='0.0.0.0', port=3000, threaded=True)