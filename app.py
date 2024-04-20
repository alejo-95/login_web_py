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

# @app.before_request
# def require_login():
#     allowed_routes = ['admin', 'registro']
#     if request.endpoint not in allowed_routes and 'username' not in session:
#         return redirect(url_for('home'))

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
        
@app.route('/logout')
def logout():
    #Remover el nombre de usuario de la sesión si está presente
    #session.pop('username', None)
    session.clear()
    return redirect(url_for('home'))

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

    # cur.execute('SELECT * FROM usuarios')
    # data2 = cur.fetchall()
    
    cur.execute('SELECT u.id, u.name, u.password, p.perfiles FROM usuarios u inner join perfiles p on u.idperfil = p.idperfiles')
    data = cur.fetchall()
    
    cur.execute('SELECT idperfiles, perfiles FROM perfiles ')
    dataOpt = cur.fetchall()
    
    cur.close()
    return render_template('Users/list_user.html', users = data, dataOpt= dataOpt)
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
    cur = mysql.connection.cursor()
    correo = request.form['txtCorreo']
    password = request.form['txtPassword']
    perfil_id = request.form['perfil']
        
    if correo == '' or password == '' or perfil_id =='':
        flash('Por favor inrgese un usuario valido','danger')
        return redirect(url_for('ListUser'))
    else:

        try:
            
            cur.execute("INSERT INTO usuarios (name, password, idperfil) VALUES (%s, %s, %s)", (correo, password, perfil_id))
            mysql.connection.commit()
            cur.close()
            flash('Usuario agregado con exito', 'success')
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
    
    if perfil == '' or state == '':
        flash('Por favor inrgese un perfil valido', 'danger')
        return redirect(url_for('ListPerfil'))
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO perfiles (perfiles, estado) VALUES (%s, %s)", (perfil, state))
            mysql.connection.commit()
            flash('Perfil agregado con exito', 'success')
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
    
    if tip == '' or state == '':
        flash('Por favor ingrese un tipo de cliente valido', 'danger')
        return redirect(url_for('ListTipClient')) 
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tipo_clientes (tipo, estado) VALUES (%s, %s)", (tip, state))
            mysql.connection.commit()
            flash('Tipo cliente agregado con exito', 'success')
            return redirect(url_for('ListTipClient'))
        except Exception as e:

            return 


#Metodos para tamaños de invernadero
#Listar
@app.route('/listar-tamanio')
def ListTamanio():
    cur=mysql.connection.cursor()

    # cur.execute('SELECT * FROM tamanios_invernadero')
    cur.execute('SELECT idtamanios, tamanio ,CASE WHEN estado = 0 THEN \'Habilitado\' WHEN estado = 1 THEN \'Deshabilitado\' END AS status FROM tamanios_invernadero')
    data = cur.fetchall()

    cur.close()
    return render_template('invernaderos/list_tamanio_inv.html', tam = data)
#Actualizar
@app.route('/updateTamanio/<id>', methods=['POST'])
def updateTamanio(id):
    if request.method == 'POST':
        tam = request.form['txtTam']
        state = request.form['txtEstado']
        
        if tam == '' or state == "":
            flash('Por favor ingrese un tamaño valido', 'danger')
            return redirect(url_for('ListTamanio'))
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE tamanios_invernadero
                SET tamanio = %s,
                    estado = %s
                WHERE idtamanios= %s
            """, (tam, state,  id))
        mysql.connection.commit()
        cur.close()
        flash('Tamaño actualizado exitosamente', 'success')
        return redirect(url_for('ListTamanio'))
#Eliminar
@app.route('/deleteTamanio/<string:id>', methods = ['POST','GET'])
def deleteTamanio(id): 
    cur=mysql.connection.cursor()
    
    cur.execute('DELETE FROM tamanios_invernadero WHERE idtamanios = {0}'.format(id))
    mysql.connection.commit()
    cur.close()
    flash('Tipo cliente eliminado exitosamente', 'success')
    return redirect(url_for('ListTamanio'))
#Agregar
@app.route('/add-tam', methods=["POST","GET"])
def addTamanio():
    tam = request.form['txtTam']
    state = request.form['txtEstado']
    
    if tam == '' or state == '':
        flash('Por favor ingrese un tamaño valido', 'danger')
        return redirect(url_for('ListTamanio')) 
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tamanios_invernadero (tamanio, estado) VALUES (%s, %s)", (tam, state))
            mysql.connection.commit()
            cur.close()
            flash('Tamaño de invernadero agregado con exito', 'success')
            return redirect(url_for('ListTamanio'))
        except Exception as e:

            return 


#Metodos para cultivos
#Listar
@app.route('/listar-cultivos')
def ListCultivo():
    cur=mysql.connection.cursor()

    # cur.execute('SELECT * FROM cultivos')
    cur.execute('SELECT idcultivos, cultivo, temp_min, temp_max ,CASE WHEN estado = 0 THEN \'Habilitado\' WHEN estado = 1 THEN \'Deshabilitado\' END AS status FROM cultivos')
    data = cur.fetchall()

    cur.close()
    return render_template('invernaderos/list_cultivos.html', temp = data)
#Actualizar
@app.route('/updateCultivo/<id>', methods=['POST'])
def updateCultivo(id):
    if request.method == 'POST':
        cul = request.form['txtCulti']
        temMin= request.form['txtTempMin']
        temMax= request.form['txtTempMax']
        #state = request.form['txtEstado']
        
        if cul == ''  or temMin == '' or temMax == "":
            flash('Por favor ingrese un cultivo valido', 'danger')
            return redirect(url_for('ListCultivo'))
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE cultivos
                SET cultivo = %s,
                    temp_min = %s,
                    temp_max = %s
                WHERE idcultivos= %s
            """, (cul, temMin, temMax,  id))
        mysql.connection.commit()
        cur.close()
        flash('Cultivo actualizado exitosamente', 'success')
        return redirect(url_for('ListCultivo'))
#Eliminar
@app.route('/deleteCultivo/<string:id>', methods = ['POST','GET'])
def deleteCultivo(id): 
    cur=mysql.connection.cursor()
    
    cur.execute('DELETE FROM cultivos WHERE idcultivos = {0}'.format(id))
    mysql.connection.commit()
    cur.close()
    flash('Cultivo eliminado exitosamente', 'success')
    return redirect(url_for('ListCultivo'))
#Agregar
@app.route('/add-cult', methods=["POST","GET"])
def addCultivo():
    cul = request.form['txtCulti']
    temMin= request.form['txtTempMin']
    temMax= request.form['txtTempMax']
    state = request.form['txtEstado']
    
    if cul == '' or state == "" or temMin == '' or temMax == "":
        flash('Por favor ingrese un cultivo valido', 'danger')
        return redirect(url_for('ListCultivo'))
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO cultivos (cultivo, temp_min, temp_max, estado) VALUES (%s,%s,%s,%s)", (cul, temMin, temMax, state))
            mysql.connection.commit()
            cur.close()
            flash('Cultivo agregado con exito', 'success')
            return redirect(url_for('ListCultivo'))
        except Exception as e:

            return 


#Metodos para clientes
#listar
@app.route('/listar-clientes')
def ListClient():
    cur=mysql.connection.cursor()

    # cur.execute('SELECT * FROM usuarios')
    # data2 = cur.fetchall()
    
    cur.execute(""" select 
                c.idclientes, c.nombre_1, c.nombre_2, c.apellido_1, c.apellido_2, 
                c.cedula, c.telefono, c.correo, tc.tipo, Case when c.estado = 0 then 'Habilitado' When c.estado = 1 then 'Deshabilitado' 
                End as status
                from clientes c
                inner join tipo_clientes tc on c.tipo_cliente = tc.idtipo_clientes""")
    data = cur.fetchall()
    
    cur.execute('SELECT idtipo_clientes, tipo FROM tipo_clientes ')
    dataOpt = cur.fetchall()
    
    cur.close()
    return render_template('tipo_cliente/clientes.html', client = data, dataOpt= dataOpt)
#Actualizar
@app.route('/updateCliente/<id>', methods=['POST'])
def updateCliente(id):
    print(request.form)
    if request.method == 'POST':
        nam1 = request.form['txtName1']
        nam2= request.form['txtName2']
        ape1= request.form['txtAp1']
        ape2 = request.form['txtAp2']
        cc = request.form['txtCc']
        tel = request.form['txtTel']
        mail = request.form['txtMail']
        tipe = request.form['tipoPersona']
        state = request.form['state']
        
        if nam1 == '' or ape1 == "" or cc == '' or tel == '' or mail =='' or tipe =='':
            flash('Por favor ingrese un cliente valido', 'danger')
            return redirect(url_for('ListClient'))
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE clientes
                SET nombre_1 = %s,
                    nombre_2 = %s,
                    apellido_1 = %s,
                    apellido_2 = %s,
                    cedula = %s,
                    telefono = %s,
                    correo = %s,
                    tipo_cliente = %s,
                    estado = %s
                WHERE idclientes= %s
            """, (nam1,nam2,ape1,ape2,cc,tel,mail,tipe,state,  id))
        mysql.connection.commit()
        cur.close()
        flash('Cliente actualizado exitosamente', 'success')
        return redirect(url_for('ListClient'))
#Elimnar
@app.route('/deleteCliente/<string:id>', methods = ['POST','GET'])
def deleteCliente(id): 
    cur=mysql.connection.cursor()
    
    cur.execute('DELETE FROM clientes WHERE idclientes = {0}'.format(id))
    mysql.connection.commit()
    cur.close()
    flash('Cliente eliminado exitosamente', 'success')
    return redirect(url_for('ListClient'))
#Agregar
@app.route('/add-clientes', methods=["POST","GET"])
def addClient():
    #print(request.form)
    nam1 = request.form['txtName1']
    nam2= request.form['txtName2']
    ape1= request.form['txtAp1']
    ape2 = request.form['txtAp2']
    cc = request.form['txtCc']
    tel = request.form['txtTel']
    mail = request.form['txtMail']
    tipe = request.form['tipoPersona']
    state = request.form['state']
    #print(nam1)
    if nam1 == '' or ape1 == "" or cc == '' or tel == '' or mail =='' or tipe =='':
        flash('Por favor ingrese un cliente valido', 'danger')
        return redirect(url_for('ListClient'))
    else:

        try:
            cur = mysql.connection.cursor()
            #cur.execute("INSERT INTO clientes (nombre_1, nombre_2,)values(%s,%s)",(nam1, nam2))
            cur.execute("INSERT INTO clientes (nombre_1, nombre_2, apellido_1, apellido_2, cedula, telefono, correo, tipo_cliente, estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (nam1,nam2,ape1,ape2,cc,tel,mail,tipe,state))
            mysql.connection.commit()
            cur.close()
            flash('Cliente agregado con exito', 'success')
            return redirect(url_for('ListClient'))
        except Exception as e:
            flash('Error al agregar el cliente: {}'.format(str(e)), 'danger')
            return redirect(url_for('ListClient'))


#Metodos para dispositivos
#listar
@app.route('/listar-dispositivos')
def ListDispo():
    cur=mysql.connection.cursor()
    
    cur.execute(""" select 
                d.iddispositivo, d.nombre, ac.accesorios, ar.arduino,
                Case when d.estado = 0 then 'Habilitado' When d.estado = 1 then 'Deshabilitado' 
                End as status
                from dispositivos d
                inner join arduinos ar on ar.idarduinos = d.idarduino
                inner join accesorios ac on ac.idaccesorios = d.idaccesorio""")
    data = cur.fetchall()
    
    cur.execute('SELECT idarduinos, arduino FROM arduinos ')
    dataOpt = cur.fetchall()
    cur.execute('SELECT idaccesorios, accesorios FROM accesorios ')
    dataOpt2 = cur.fetchall()
    
    cur.close()
    return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2)
#Agregar
@app.route('/add-dispo', methods=["POST","GET"])
def addDispo():
    #print(request.form)
    disp = request.form['txtDispo']
    acce= request.form['accesorio']
    ardui= request.form['arduino']
    state = request.form['state']
    #print(nam1)
    if disp == '' or acce == "" or ardui == '' or state == '':
        flash('Por favor ingrese un dispositivo valido', 'danger')
        return redirect(url_for('ListDispo'))
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO dispositivos (nombre, idaccesorio,idarduino,estado)values(%s,%s,%s,%s)",(disp,acce,ardui,state))
            mysql.connection.commit()
            cur.close()
            flash('Dispositivo agregado con exito', 'success')
            return redirect(url_for('ListDispo'))
        except Exception as e:
            flash('Error al agregar el dispositivo: {}'.format(str(e)), 'danger')
            return redirect(url_for('ListDispo'))
#Actualizar
@app.route('/updateDispo/<id>', methods=['POST'])
def updateDispo(id):
    print(request.form)
    if request.method == 'POST':
        disp = request.form['txtDispo']
        acce= request.form['accesorio']
        ardui= request.form['arduino']
        state = request.form['state']
        
        if disp == '' or acce == "" or ardui == '' or state == '':
            flash('Por favor ingrese un dispositivo valido', 'danger')
            return redirect(url_for('ListDispo'))
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE dispositivos
                SET nombre = %s,
                    idaccesorio = %s,
                    idarduino = %s,
                    estado = %s
                WHERE iddispositivo= %s
            """, (disp,acce,ardui,state,  id))
        mysql.connection.commit()
        cur.close()
        flash('Dispositivo actualizado exitosamente', 'success')
        return redirect(url_for('ListDispo'))
#Elimnar
@app.route('/deleteDispo/<string:id>', methods = ['POST','GET'])
def deleteDispo(id): 
    cur=mysql.connection.cursor()
    
    cur.execute('DELETE FROM dispositivos WHERE iddispositivo = {0}'.format(id))
    mysql.connection.commit()
    cur.close()
    flash('Dispositivo eliminado exitosamente', 'success')
    return redirect(url_for('ListDispo'))



if __name__ == '__main__':
    app.secret_key="projectoU"
    app.run(debug=True,host='0.0.0.0', port=3000, threaded=True)