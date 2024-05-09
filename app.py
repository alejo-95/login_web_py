from flask import Flask
from flask import render_template, redirect, request, Response, session, url_for, flash
from flask_mysqldb import MySQL
#from app import app, mysql
import mysql.connector
import re


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
                return render_template("menu/admin.html")
            elif session['idperfil'] == 2:
                return render_template('menu/admin.html')
        
        else:
            flash('El usuario y/o la contraseña son incorrectos', 'danger')
            return render_template('index.html')    

#Salir
@app.route('/logout')
def logout():
    #Remover el nombre de usuario de la sesión si está presente
    #session.pop('username', None)
    session.clear()
    return redirect(url_for('home'))

#Renderiza vista registro
@app.route('/registro')
def initRegister():
    cur=mysql.connection.cursor()
    cur.execute('SELECT idtipo_clientes, tipo FROM tipo_clientes ')
    dataOpt = cur.fetchall()
    cur.close()
    return render_template('login_register/registro.html', cliente=True, dataOpt= dataOpt)
#Crear Cliente registro
@app.route('/crear_registro', methods=["GET", "POST"])
def registro():
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
    #print(cc)
    cur=mysql.connection.cursor()
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
    
    if not validar_cc(cc):
        flash('La cédula ingresada no es valida', 'danger')
        return render_template('login_register/registro.html',client = data, ccErr=True,dataOpt=dataOpt, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail, cliente= True)
    
    if not validar_nombre(nam1):
        flash('El nombre ingresado no es valido', 'danger')
        return render_template('login_register/registro.html',client = data, nam1Err=True,dataOpt=dataOpt, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail, cliente= True)
        #return redirect(url_for('ListClient'))
    
    if nam2 != '':
        if not validar_nombre(nam2):
            flash('El segundo nombre ingresado no es valido', 'danger')
            return render_template('login_register/registro.html',client = data, nam2Err=True,dataOpt=dataOpt, add_modal=True,
            cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail,cliente= True)
            #return redirect(url_for('ListClient'))
        
    if not validar_nombre(ape1):
        flash('El apellido ingresado no es valido', 'danger')
        return render_template('login_register/registro.html',client = data, ape1Err=True,dataOpt=dataOpt, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail, cliente= True)
        #return redirect(url_for('ListClient'))
    
    if nam2 != '':
        if not validar_nombre(ape2):
            flash('El segundo apellido ingresado no es valido', 'danger')
            return render_template('login_register/registro.html',client = data, ape2Err=True,dataOpt=dataOpt, add_modal=True,
            cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail, cliente= True)
            #return redirect(url_for('ListClient'))
        
    if not validar_celular(tel):
        flash('El celular ingresado no es valido', 'danger')
        return render_template('login_register/registro.html',client = data, telErr=True,dataOpt=dataOpt, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail, cliente= True)
        #return redirect(url_for('ListClient'))
    
    if not validar_correo(mail):
        flash('El correo inrgesado es incorrecto', 'danger')
        return render_template('login_register/registro.html',client = data, mailErr=True,dataOpt=dataOpt, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail, cliente= True)
        #return redirect(url_for('ListClient'))
    
    if nam1 == '' or ape1 == "" or cc == '' or tel == '' or mail =='' or tipe =='':
        flash('Por favor ingrese un cliente valido', 'danger')
        return render_template('login_register/registro.html',client = data, dupliErr=True,dataOpt=dataOpt, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail, cliente= True)
        #return redirect(url_for('ListClient'))
    
    if not cc =='':
        cur = mysql.connection.cursor()
        cur.execute('Select cedula from clientes where cedula = {0}'.format(cc))
        busquedaCC = cur.fetchone()
        cur.close()
    
    
    if  busquedaCC: 
        flash(f'El cliente con cédula {cc} ya se encuentra creado', 'danger')
        #return redirect(url_for('ListClient'))
        return render_template('login_register/registro.html',client = data, dupliErr=True,dataOpt=dataOpt, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail, cliente= True)
    else:

        try:
            cur = mysql.connection.cursor()
            #cur.execute("INSERT INTO clientes (nombre_1, nombre_2,)values(%s,%s)",(nam1, nam2))
            cur.execute("INSERT INTO clientes (nombre_1, nombre_2, apellido_1, apellido_2, cedula, telefono, correo, tipo_cliente, estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (nam1,nam2,ape1,ape2,cc,tel,mail,tipe,state))
            mysql.connection.commit()
            cur.close()
            flash('Cliente agregado con exito, por favor cree el usuario', 'success')
            return render_template('login_register/registro.html',dupliErr=True,usuario=True, cliente=False, cc=cc)
        except Exception as e:
            if e.errno == 1451:
                flash('No se puede eliminar el cliente porque está relacionado con otros registros.', 'danger')
            else:
                flash('Error al agregar el cliente: {}'.format(str(e)), 'danger')
            
            return redirect(url_for('home'))
    
    #return render_template('Login_register/registro.html')
#Crear usuario en registro
@app.route('/create-registro/<id>', methods=["GET","POST"])
def createRegister(id):
    correo = request.form['txtCorreo']
    password = request.form['txtPassword']
    #perfil_id = request.form['perfil']
    cliente = id
    print(request.form, cliente)
    
    cur = mysql.connection.cursor()
    cur.execute('Select name from usuarios where name = %s',(correo,))
    busquedaCC = cur.fetchone()
    cur.execute('SELECT u.id, u.name, u.password, p.perfiles FROM usuarios u inner join perfiles p on u.idperfil = p.idperfiles')
    data = cur.fetchall() 
    cur.execute('SELECT idperfiles, perfiles FROM perfiles ')
    dataOpt = cur.fetchall()
    cur.close()
    
    if  busquedaCC: 
        flash(f'El usuario {correo} ya se encuentra creado', 'danger')
        return render_template('login_register/registro.html', users = data, dataOpt= dataOpt, correo=correo, dupliErr= True, add_modal=True, usuario = True)
    
    if not validar_usuario(correo):
        flash('El usuario ingresado no es valido valido','danger')
        return render_template('login_register/registro.html', users = data, dataOpt= dataOpt, correo=correo, correoErr= True, add_modal=True, usuario = True)
    
    if  password == '':
        flash('Por favor inrgese un usuario valido','danger')
        return render_template('login_register/registro.html', users = data, dataOpt= dataOpt, correo=correo, contraErr= True, add_modal=True, usuario = True)
    
    # if perfil_id == '':
    #     flash('Por favor inrgese un perfil valido','danger')
    #     return render_template('login_register/registro.html', users = data, dataOpt= dataOpt, correo=correo, perfilErr= True, add_modal=True)
    else:
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (name, password, idperfil, cliente) VALUES (%s, %s, 2,%s)", (correo, password, cliente,))
            mysql.connection.commit()
            cur.close()
            flash('Usuario agregado con exito', 'success')
            #return render_template('index.html')
            return redirect(url_for('home'))
        except Exception as e:
            flash('Error al agregar un usuario', 'danger')
            print(e)
            return redirect(url_for('home'))


#recuperar contraseña
@app.route('/rec-contraseña')
def ForgotPassword():
    return render_template('Login_register/recu_contraseña.html')
#Actualizar contraseña
@app.route('/newPassword', methods=['POST', 'GET'])
def NewPassword():
    cc = request.form['txtCc']
    user = request.form['txtCorreo']
    pass1 = request.form['txtPassword']
    pass2 = request.form['txtPassword2']
    print(request.form)
    print(cc)
    
    cur = mysql.connection.cursor()
    cur.execute('Select cedula from clientes where cedula = %s',(cc,))
    existeCC = cur.fetchone()
    cur.execute('Select name from usuarios where cliente = %s and name = %s',(cc,user,))
    existeUser = cur.fetchone()
    cur.close()
    
    if not existeCC:
        flash('El cliente ingresado no existe', 'danger')
        return render_template('Login_register/recu_contraseña.html',cc=cc, user=user, ccErr=True)
            
    if not existeUser:
        flash('El usuario ingresado no existe para ese cliente', 'danger')
        return render_template('Login_register/recu_contraseña.html',cc=cc, user=user, correoErr=True)
        
    if pass1 == '':
        flash('Por favor ingrese una contraseña', 'danger')
        return render_template('Login_register/recu_contraseña.html',cc=cc, user=user, contraErr=True)
        
    
    if not pass1 == pass2:
        flash('Las contraseñas deben ser iguales', 'danger')
        return render_template('Login_register/recu_contraseña.html',cc=cc, user=user, contraErr=True)
        
    if existeCC and existeUser and pass1 != '' and pass1 == pass2:          
        cur = mysql.connection.cursor()
        cur.execute('update usuarios set password = %s where cliente = %s and name = %s',(pass1,cc, user,))
        mysql.connection.commit()
        cur.close()
        flash('Contraseña actualizada con exito', 'success')
        return redirect(url_for('home'))      



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
#actualizar
@app.route('/update/<id>', methods=['POST'])
def update_employee(id):
    if request.method == 'POST':
        name = request.form['txtCorreo']
        password = request.form['txtPassword']
        
        cur = mysql.connection.cursor()
        cur.execute('Select name from usuarios where name = %s',(name,))
        busquedaCC = cur.fetchone()
        cur.execute('Select name from usuarios where id = %s',(id,))
        repe = cur.fetchone()
        cur.execute('SELECT u.id, u.name, u.password, p.perfiles FROM usuarios u inner join perfiles p on u.idperfil = p.idperfiles')
        data = cur.fetchall() 
        cur.execute('SELECT idperfiles, perfiles FROM perfiles ')
        dataOpt = cur.fetchall()
        cur.close()
    
        
        
        if not validar_usuario(name):
            flash('El usuario ingresado no es valido valido','danger')
            return render_template('Users/list_user.html', users = data, dataOpt= dataOpt,  correoErrEdit= True, edit_modal=id)
        
        if  password == '':
            flash('Por favor inrgese un usuario valido','danger')
            return render_template('Users/list_user.html', users = data, dataOpt= dataOpt,  contraErrEdit= True, edit_modal=id)
        
        if  busquedaCC: 
            flash(f'El usuario {name} ya se encuentra creado', 'danger')
            return render_template('Users/list_user.html', users = data, dataOpt= dataOpt, dupliErrEdit= True, edit_modal=id)
        
        if busquedaCC:
            if repe['name'] == name:
                flash('Usuario sin cambios detectados', 'success')
                return redirect(url_for('ListUser'))
            elif busquedaCC['name']:
                flash(f'El usuario {name} ya se encuentra creado', 'danger')
                return redirect(url_for('ListUser'))           
        
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE usuarios
                SET name = %s,
                    password = %s
                WHERE id = %s
            """, (name, password,  id))
        mysql.connection.commit()
        cur.close()
        flash('Usuario actualizado exitosamente','success')
        return redirect(url_for('ListUser'))
#Eliminar 
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_employee(id):
    
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM usuarios WHERE id = {0}'.format(id))
        mysql.connection.commit()
        flash('Usuario eliminado exitosamente','success')
        return redirect(url_for('ListUser'))

    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el usuario porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el usuario: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
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
    perfil_id = request.form['perfil']
    cc = request.form['txtCedula']
    #print(request.form)
    
    cur = mysql.connection.cursor()
    cur.execute('Select name from usuarios where name = %s',(correo,))
    busquedaCC = cur.fetchone()
    cur.execute('SELECT u.id, u.name, u.password, p.perfiles FROM usuarios u inner join perfiles p on u.idperfil = p.idperfiles')
    data = cur.fetchall() 
    cur.execute('SELECT idperfiles, perfiles FROM perfiles ')
    dataOpt = cur.fetchall()
    cur.execute('Select cedula from clientes where cedula =  %s',(cc,))
    cedula = cur.fetchone()
    cur.close()
    
    if not cedula:
        flash('El cliente ingresado no es valido valido','danger')
        return render_template('Users/list_user.html', users = data, dataOpt= dataOpt, correo=correo, ccErr= True, add_modal=True)
    
    if  busquedaCC: 
        flash(f'El usuario {correo} ya se encuentra creado', 'danger')
        return render_template('Users/list_user.html', users = data, dataOpt= dataOpt, correo=correo, dupliErr= True, add_modal=True)
    
    if not validar_usuario(correo):
        flash('El usuario ingresado no es valido valido','danger')
        return render_template('Users/list_user.html', users = data, dataOpt= dataOpt, correo=correo, correoErr= True, add_modal=True)
    
    if  password == '':
        flash('Por favor inrgese un usuario valido','danger')
        return render_template('Users/list_user.html', users = data, dataOpt= dataOpt, correo=correo, contraErr= True, add_modal=True)
    
    if perfil_id == '':
        flash('Por favor inrgese un perfil valido','danger')
        return render_template('Users/list_user.html', users = data, dataOpt= dataOpt, correo=correo, perfilErr= True, add_modal=True)
    else:
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (name, password, idperfil, cliente) VALUES (%s, %s, %s, %s)", (correo, password, perfil_id, cc))
            mysql.connection.commit()
            cur.close()
            flash('Usuario agregado con exito', 'success')
            return redirect(url_for('ListUser'))
        except Exception as e:
            flash('Error al agregar un usuario', 'danger')
            print(e)
            return redirect(url_for('ListUser'))
#Inhabilitar
@app.route('/InhabilUser/<string:id>', methods = ['POST','GET'])
def InhaUser(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update usuarios  set estado = 1 WHERE id = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Perfil inhabilitado exitosamente', 'success')
        return redirect(url_for('ListUser'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede inhabilitar el usuario porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al inhabilitar el usuario: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListUser'))

#Metodos para perfil
#listar
@app.route('/listar-perfiles')
def ListPerfil():
    cur=mysql.connection.cursor()

    cur.execute("""SELECT idperfiles,perfiles,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM perfiles""")
    data = cur.fetchall()

    cur.close()
    return render_template('perfil/list_perfil.html', perfil = data)
#Actualizar
@app.route('/updatePerfil/<id>', methods=['POST'])
def updatePerfil(id):
    if request.method == 'POST':
        perfil = request.form['txtPerfil']
        #state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select perfiles from perfiles where perfiles = %s',(perfil,))
        busquedaCC = cur.fetchone()
        cur.execute('Select perfiles from perfiles where idperfiles = %s',(id,))
        repe = cur.fetchone()
        cur.execute("""SELECT idperfiles,perfiles,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM perfiles""")
        data = cur.fetchall()
        cur.close()
    
            
        if not validar_nombre(perfil):
            flash('Por favor ingrese un perfil valido', 'danger')
            return render_template('perfil/list_perfil.html', perfil = data, perfilErrEdit=True, edit_modal=id)
        
        if busquedaCC:
            if repe['perfiles'] == perfil:
                flash('Perfil sin cambios detectados', 'success')
                return redirect(url_for('ListPerfil'))
            elif busquedaCC['perfiles']:
                flash(f'El perfil {perfil} ya se encuentra creado', 'danger')
                return render_template('perfil/list_perfil.html', perfil = data, dupliErrEdit=True, edit_modal=id) 
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE perfiles
                SET perfiles = %s
                    
                WHERE idperfiles = %s
            """, (perfil,  id))
        mysql.connection.commit()
        flash('Perfil actualizado exitosamente','success')
        return redirect(url_for('ListPerfil'))
#Eliminar
@app.route('/deletePerfil/<string:id>', methods = ['POST','GET'])
def deletePerfil(id): 
    
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM perfiles WHERE idperfiles = {0}'.format(id))
        mysql.connection.commit()
        flash('Perfil eliminado exitosamente','success')
        return redirect(url_for('ListPerfil'))
    except Exception  as e:
            if '1451' in str(e):
                flash('No se puede eliminar el perfil porque está relacionado con otros registros.', 'warning')
            else:
                flash('Error al eliminar el perfil: {}'.format(str(e)), 'warning')
    finally:
            cur.close()
    return redirect(url_for('ListPerfil'))
#Agregar
@app.route('/add-perfiles', methods=["POST","GET"])
def addPerfil():
    perfil = request.form['txtPerfil']
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select perfiles from perfiles where perfiles = %s',(perfil,))
    busquedaCC = cur.fetchone()
    cur.execute("""SELECT idperfiles,perfiles,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM perfiles""")
    data = cur.fetchall()
    cur.close()
    
    
    if not validar_nombre(perfil):
        flash('Por favor ingrese un perfil valido', 'danger')
        return render_template('perfil/list_perfil.html', perfil = data, perfilErr=True, add_modal=True, perfilTxt=perfil)
    
    
    if  busquedaCC: 
        flash(f'El perfil {perfil} ya se encuentra creado', 'danger')
        return render_template('perfil/list_perfil.html', perfil = data, dupliErr=True, add_modal=True, perfilTxt=perfil) 

    else:
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO perfiles (perfiles, estado) VALUES (%s, %s)", (perfil, state))
            mysql.connection.commit()
            flash('Perfil agregado con exito', 'success')
            return redirect(url_for('ListPerfil'))
        except Exception as e:
            flash(f'error al agregar el perfil {e}')
            return 
#Inhabilitar
@app.route('/InhabilPerfil/<string:id>', methods = ['POST','GET'])
def InhaPerfil(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update perfiles  set estado = 1 WHERE idperfiles = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Perfil inhabilitado exitosamente', 'success')
        return redirect(url_for('ListPerfil'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede inhabilitar el perfil porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al inhabilitar el perfil: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListPerfil'))


#Metodos para sensores
#Listar
@app.route('/listar-acce')
def ListAcce():
    cur=mysql.connection.cursor()

    cur.execute("""SELECT idaccesorios,accesorios,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_sensor""")
    data = cur.fetchall()

    cur.close()
    return render_template('accesorios/list_acce.html', acce = data)
#Actualizar
@app.route('/updateAcce/<id>', methods=['POST'])
def updateAcce(id):
    if request.method == 'POST':
        acce = request.form['txtAcce']
        #state = request.form['state']
        #print(state)
        
        cur = mysql.connection.cursor()
        cur.execute('Select accesorios from tipo_sensor where accesorios = %s',(acce,))
        busquedaCC = cur.fetchone()
        cur.execute('Select accesorios, estado from tipo_sensor where idaccesorios = %s',(id,))
        repe = cur.fetchone()
        cur.execute("""SELECT idaccesorios,accesorios,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_sensor""")
        data = cur.fetchall()
        cur.close()

        if not validar_espacios(acce):
            flash('Por favor ingrese un accesorio valido','danger')
            return render_template('accesorios/list_acce.html', acce = data, acceErrEdit=True, edit_modal=id)
        
        if busquedaCC:
            if repe['accesorios'] == acce:
                flash('Accesorio sin cambios detectados', 'success')
                return redirect(url_for('ListAcce'))
            elif busquedaCC['accesorios']:
                flash(f'El accesorio {acce} ya se encuentra creado', 'danger')
                return render_template('accesorios/list_acce.html', acce = data, dupliErrEdit=True, edit_modal=id)  

        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE tipo_sensor
                SET accesorios = %s
                    
                WHERE idaccesorios = %s
            """, (acce,  id))
        mysql.connection.commit()
        flash('Accesorio actualizado exitosamente','success')
        return redirect(url_for('ListAcce'))
#Eliminar
@app.route('/deleteAcce/<string:id>', methods = ['POST','GET'])
def deleteAcce(id): 
    
    try:
        cur=mysql.connection.cursor()   
        cur.execute('DELETE FROM tipo_sensor WHERE idaccesorios = {0}'.format(id))
        mysql.connection.commit()
        flash('Accesorio eliminado exitosamente')
        return redirect(url_for('ListAcce'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el accesorio porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el accesorio: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListAcce'))
#Agregar
@app.route('/add-acce', methods=["POST","GET"])
def addAcce():
    acce = request.form['txtAcce']
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select accesorios from tipo_sensor where accesorios = %s',(acce,))
    busquedaCC = cur.fetchone()
    cur.execute("""SELECT idaccesorios,accesorios,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_sensor""")
    data = cur.fetchall()
    cur.close()
    
    if not validar_espacios(acce):
        flash('Por favor ingrese un accesorio valido','danger')
        return render_template('accesorios/list_acce.html', acce = data, acceErr=True, add_modal=True, acceTxt= acce)   
        
    if  busquedaCC: 
        flash(f'El accesorio {acce} ya se encuentra creado', 'danger')
        return render_template('accesorios/list_acce.html', acce = data, dupliErr=True, add_modal=True, acceTxt= acce)  
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tipo_sensor (accesorios, estado) VALUES (%s, %s)", (acce, state))
            mysql.connection.commit()
            flash('Accesorio agregado con exito')
            return redirect(url_for('ListAcce'))
        except Exception as e:
            flash(f'Error al agregar el accesorio{e}')
            return 
#Inhabilitar
@app.route('/InhabilAcce/<string:id>', methods = ['POST','GET'])
def InhaAcce(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update tipo_sensor  set estado = 1 WHERE idaccesorios = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Accesorio inhabilitado exitosamente', 'success')
        return redirect(url_for('ListAcce'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el accesorio porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el accesorio: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListAcce'))

#Metodos para arduinos
#Listar
@app.route('/listar-ard')
def ListArd():
    cur=mysql.connection.cursor()

    cur.execute("""SELECT idarduinos,arduino,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_arduino""")
    data = cur.fetchall()

    cur.close()
    return render_template('arduinos/list_arduino.html', ard = data)
#Actualizar
@app.route('/updateArd/<id>', methods=['POST'])
def updateArd(id):
    if request.method == 'POST':
        ard = request.form['txtMot']
        #state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select arduino from tipo_arduino where arduino = %s',(ard,))
        busquedaCC = cur.fetchone()
        cur.execute('Select arduino from tipo_arduino where idarduinos = %s',(id,))
        repe = cur.fetchone()
        cur.execute("""SELECT idarduinos,arduino,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_arduino""")
        data = cur.fetchall()
        cur.close()
    
        if not validar_espacios(ard):
            flash('Por favor ingrese una arduino valido','danger')
            return render_template('arduinos/list_arduino.html', ard = data, ardErrEdit=True, edit_modal=id)   
        
        if  ard == '':
            flash('Por favor ingrese un arduino valido','danger')
            return redirect(url_for('ListArd'))
        
        if busquedaCC:
            if repe['arduino'] == ard:
                flash('Arduino sin cambios detectados', 'success')
                return redirect(url_for('ListArd'))
            elif busquedaCC['arduino']:
                flash(f'El arduino {ard} ya se encuentra creado', 'danger')
                return render_template('arduinos/list_arduino.html', ard = data, dupliErrEdit=True, edit_modal=id)     

        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE tipo_arduino
                SET arduino = %s
                    
                WHERE idarduinos= %s
            """, (ard,  id))
        mysql.connection.commit()
        flash('Arduino actualizado exitosamente','success')
        return redirect(url_for('ListArd'))
#Eliminar
@app.route('/deleteArd/<string:id>', methods = ['POST','GET'])
def deleteArd(id): 
    
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM tipo_arduino WHERE idarduinos = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Arduino eliminado exitosamente','success')
        return redirect(url_for('ListArd'))
    
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el arduino porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el arduino: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListArd'))
#Agregar
@app.route('/add-ard', methods=["POST","GET"])
def addArd():
    ard = request.form['txtArd']
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select arduino from arduinos where arduino = %s',(ard,))
    busquedaCC = cur.fetchone()
    cur.execute("""SELECT idarduinos,arduino,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_arduino""")
    data = cur.fetchall()
    cur.close()
    
    if not validar_espacios(ard):
        flash('Por favor ingrese una arduino valido','danger')
        return render_template('arduinos/list_arduino.html', ard = data, ardErr=True, add_modal=True, ardTxt= ard)
    
    if  busquedaCC: 
        flash(f'El arduino {ard} ya se encuentra creado', 'danger')
        return render_template('arduinos/list_arduino.html', ard = data, dupliErr=True, add_modal=True, ardTxt= ard)
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO arduinos (arduino, estado) VALUES (%s, %s)", (ard, state))
            mysql.connection.commit()
            flash('Arduino agregado con exito','success')
            return redirect(url_for('ListArd'))
        except Exception as e:
            flash('Error al agregar el arduino','danger')
            return redirect(url_for('ListArd'))
#Inhabilitar
@app.route('/InhabilArd/<string:id>', methods = ['POST','GET'])
def InhaArd(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update tipo_arduino  set estado = 1 WHERE idarduinos = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Arduino inhabilitado exitosamente', 'success')
        return redirect(url_for('ListArd'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede inhabilitar el Arduino porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al inhabilitar el Arduino: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListArd'))


#Metodos para motor
#Listar
@app.route('/listar-mot')
def ListMotor():
    cur=mysql.connection.cursor()

    cur.execute("""SELECT idtipo_motor,tipo_motor,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_motor""")
    data = cur.fetchall()

    cur.close()
    return render_template('motores/list_motores.html', mot = data)
#Actualizar
@app.route('/updateMot/<id>', methods=['POST'])
def updateMot(id):
    if request.method == 'POST':
        mot = request.form['txtMot']
        #state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select tipo_motor from tipo_motor where tipo_motor = %s',(mot,))
        busquedaCC = cur.fetchone()
        cur.execute('Select tipo_motor from tipo_motor where idtipo_motor = %s',(id,))
        repe = cur.fetchone()
        cur.execute("""SELECT idtipo_motor,tipo_motor,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_motor""")
        data = cur.fetchall()
        cur.close()
    
        if not validar_espacios(mot):
            flash('Por favor ingrese un motor valido','danger')
            return render_template('motores/list_motores.html', mot = data, motErrEdit=True, edit_modal=id)   
        
        # if  mot == '':
        #     flash('Por favor ingrese un motor valido','danger')
        #     return redirect(url_for('ListArd'))
        
        if busquedaCC:
            if repe['tipo_motor'] == mot:
                flash('Motor sin cambios detectados', 'success')
                return redirect(url_for('ListMotor'))
            elif busquedaCC['tipo_motor']:
                flash(f'El motor {mot} ya se encuentra creado', 'danger')
                return render_template('motores/list_motores.html', mot = data, dupliErrEdit=True, edit_modal=id)     

        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE tipo_motor
                SET tipo_motor = %s
                    
                WHERE idtipo_motor= %s
            """, (mot,  id))
        mysql.connection.commit()
        flash('Motor actualizado exitosamente','success')
        return redirect(url_for('ListMotor'))
#Eliminar
@app.route('/deleteMot/<string:id>', methods = ['POST','GET'])
def deleteMot(id): 
    
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM tipo_motor WHERE idtipo_motor = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Motor eliminado exitosamente','success')
        return redirect(url_for('ListMotor'))
    
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el motor porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el motor: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListMotor'))
#Agregar
@app.route('/add-mot', methods=["POST","GET"])
def addMot():
    mot = request.form['txtMot']
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select tipo_motor from tipo_motor where tipo_motor = %s',(mot,))
    busquedaCC = cur.fetchone()
    cur.execute("""SELECT idtipo_motor,tipo_motor,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_motor""")
    data = cur.fetchall()
    cur.close()
    
    if not validar_espacios(mot):
        flash('Por favor ingrese un motor valido','danger')
        return render_template('motores/list_motores.html', mot = data, motErr=True, add_modal=True, motTxt= mot)
    
    if  busquedaCC: 
        flash(f'El motor {mot} ya se encuentra creado', 'danger')
        return render_template('motores/list_motores.html', mot = data, dupliErr=True, add_modal=True, motTxt= mot)
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tipo_motor (tipo_motor, estado) VALUES (%s, %s)", (mot, state))
            mysql.connection.commit()
            flash('Motor agregado con exito','success')
            return redirect(url_for('ListMotor'))
        except Exception as e:
            flash('Error al agregar el motor','danger')
            return redirect(url_for('ListMotor'))
#Inhabilitar
@app.route('/InhabilMot/<string:id>', methods = ['POST','GET'])
def InhaMot(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update tipo_motor  set estado = 1 WHERE idtipo_motor = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Motor inhabilitado exitosamente', 'success')
        return redirect(url_for('ListMotor'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede inhabilitar el motor porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al inhabilitar el motor: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListMotor'))



#Metodos para tipo_cliente
#Listar
@app.route('/listar-tipClient')
def ListTipClient():
    cur=mysql.connection.cursor()
    cur.execute("""SELECT idtipo_clientes,tipo,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_clientes""")
    data = cur.fetchall()
    cur.close()
    return render_template('tipo_cliente/list_tipo_cliente.html', tip = data)
#Actualizar
@app.route('/updateTipClient/<id>', methods=['POST'])
def updateTipClient(id):
    if request.method == 'POST':
        tip = request.form['txtTip']
        #state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select tipo from tipo_clientes where tipo = %s',(tip,))
        busquedaCC = cur.fetchone()
        cur.execute('Select tipo from tipo_clientes where idtipo_clientes = %s',(id,))
        repe = cur.fetchone()
        cur.execute("""SELECT idtipo_clientes,tipo,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_clientes""")
        data = cur.fetchall()
        cur.close()
    
        if not validar_espacios(tip):
            flash('Por favor ingrese un tipo cliente válido', 'danger')
            return render_template('tipo_cliente/list_tipo_cliente.html', tipErr=True, edit_modal=id, tip= data,tipe=tip)
        
        if  tip == '':
            flash('Por favor ingrese un tipo cliente valido','danger')
            return redirect(url_for('ListTipClient'))
        
        if busquedaCC:
            if repe['tipo'] == tip:
                flash('Tipo cliente sin cambios detectados', 'success')
                return redirect(url_for('ListTipClient'))
            elif busquedaCC['tipo']:
                flash(f'El tipo cliente {tip} ya se encuentra creado', 'danger')
                return render_template('tipo_cliente/list_tipo_cliente.html', dupliErr=True, edit_modal=id, tip= data)     
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE tipo_clientes
                SET tipo = %s
                    
                WHERE idtipo_clientes= %s
            """, (tip,  id))
        mysql.connection.commit()
        flash('Tipo cliente actualizado exitosamente','success')
        return redirect(url_for('ListTipClient'))
#Eliminar
@app.route('/deleteTipClient/<string:id>', methods = ['POST','GET'])
def deleteTipClient(id): 
    cur=mysql.connection.cursor()
    
    try:
        cur.execute('DELETE FROM tipo_clientes WHERE idtipo_clientes = {0}'.format(id))
        mysql.connection.commit()
        flash('Tipo cliente eliminado exitosamente')
        return redirect(url_for('ListTipClient'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el tipo cliente porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el tipo cliente: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListTipClient'))
#Agregar
@app.route('/add-tip', methods=["POST","GET"])
def addTipClient():
    tip = request.form['txtTip']
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select tipo from tipo_clientes where tipo = %s',(tip,))
    busquedaCC = cur.fetchone()
    cur.execute("""SELECT idtipo_clientes,tipo,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_clientes""")
    data = cur.fetchall()
    cur.close()
    
    if not validar_espacios(tip):
        flash('Por favor ingrese un tipo cliente válido', 'danger')
        return render_template('tipo_cliente/list_tipo_cliente.html', tipErr=True, add_modal=True, tip= data, tipe=tip)
    
    if  busquedaCC: 
        flash(f'El tipo cliente {tip} ya se encuentra creado', 'danger')
        return render_template('tipo_cliente/list_tipo_cliente.html', dupliErr=True, add_modal=True, tip= data)   
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tipo_clientes (tipo, estado) VALUES (%s, %s)", (tip, state))
            mysql.connection.commit()
            flash('Tipo cliente agregado con exito', 'success')
            return redirect(url_for('ListTipClient'))
        except Exception as e:

            return 
#Inhabilitar
@app.route('/InhabilTipClient/<string:id>', methods = ['POST','GET'])
def InhaTipClient(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update tipo_clientes  set estado = 1 WHERE idtipo_clientes = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Tipo Cliente inhabilitado exitosamente', 'success')
        return redirect(url_for('ListTipClient'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el tipo cliente porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el cliente: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListTipClient'))

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
        #state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select tamanio from tamanios_invernadero where tamanio = %s',(tam,))
        busquedaCC = cur.fetchone()
        cur.execute('Select tamanio from tamanios_invernadero where idtamanios = %s',(id,))
        repe = cur.fetchone()
        cur.execute('SELECT idtamanios, tamanio ,CASE WHEN estado = 0 THEN \'Habilitado\' WHEN estado = 1 THEN \'Deshabilitado\' END AS status FROM tamanios_invernadero')
        data = cur.fetchall()
        cur.close()
    
        if not validar_digitosDecimales(tam):
            flash('Por favor ingrese un tamaño valido', 'danger')
            return render_template('invernaderos/list_tamanio_inv.html', tamErrEdit=True, edit_modal=id, tam= data, tamn=tam)
        
        if  tam == '':
            flash('Por favor ingrese un tamaño valido','danger')
            return redirect(url_for('ListTamanio'))
        
        if busquedaCC:
            if repe['tamanio'] == tam:
                flash('Tamaño sin cambios detectados', 'success')
                return redirect(url_for('ListTamanio'))
            elif busquedaCC['tamanio']:
                flash(f'El la medida {tam} metros ya se encuentra creado', 'danger')
                return render_template('invernaderos/list_tamanio_inv.html', tamErrEdit=True, edit_modal=id, tam= data, tamn=tam) 
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE tamanios_invernadero
                SET tamanio = %s
                
                WHERE idtamanios= %s
            """, (tam,  id))
        mysql.connection.commit()
        cur.close()
        flash('Tamaño actualizado exitosamente', 'success')
        return redirect(url_for('ListTamanio'))
#Eliminar
@app.route('/deleteTamanio/<string:id>', methods = ['POST','GET'])
def deleteTamanio(id): 
    cur=mysql.connection.cursor()
    try:
        cur.execute('DELETE FROM tamanios_invernadero WHERE idtamanios = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Tamaño eliminado exitosamente', 'success')
        return redirect(url_for('ListTamanio'))    
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar la medida porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar la medida: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListTamanio'))
#Agregar
@app.route('/add-tam', methods=["POST","GET"])
def addTamanio():
    tam = request.form['txtTam']
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select tamanio from tamanios_invernadero where tamanio = %s',(tam,))
    busquedaCC = cur.fetchone()
    cur.execute('SELECT idtamanios, tamanio ,CASE WHEN estado = 0 THEN \'Habilitado\' WHEN estado = 1 THEN \'Deshabilitado\' END AS status FROM tamanios_invernadero')
    data = cur.fetchall()
    cur.close()
    
    if not validar_digitosDecimales(tam):
        flash('Por favor ingrese un tamaño valido', 'danger')
        return render_template('invernaderos/list_tamanio_inv.html', tamErr=True, add_modal=True, tam= data, tamn=tam)
    
    if  busquedaCC: 
        flash(f'El la medida {tam} metros ya se encuentra creada', 'danger')
        return render_template('invernaderos/list_tamanio_inv.html', dupliErr=True, add_modal=True, tam= data, tamn=tam)
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
#Inhabilitar
@app.route('/InhabilTamanio/<string:id>', methods = ['POST','GET'])
def InhaTtamanio(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update tamanios_invernadero  set estado = 1 WHERE idtamanios = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Tamaño inhabilitado exitosamente', 'success')
        return redirect(url_for('ListTamanio'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede inhabilitar el tamaño porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al inbailitar el tamaño: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListTamanio'))

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
        temMin = request.form['txtTempMin']
        temMax = request.form['txtTempMax']
        #state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT cultivo, temp_min, temp_max FROM cultivos WHERE idcultivos = %s', (id,))
        repe = cur.fetchone()
        cur.execute('SELECT idcultivos, cultivo, temp_min, temp_max ,CASE WHEN estado = 0 THEN \'Habilitado\' WHEN estado = 1 THEN \'Deshabilitado\' END AS status FROM cultivos')
        data = cur.fetchall()
        cur.close()
        
        
        if not validar_espacios(cul):
            flash('Por favor ingrese un cultivo valido', 'danger')
            return render_template('invernaderos/list_cultivos.html', culErrEdit=True, edit_modal=id, temp= data)
        
        if not validar_digitosDecimales(temMin):
            flash('Por favor ingrese una temperatura valida valida', 'danger')
            return render_template('invernaderos/list_cultivos.html', temMinErrEdit=True, edit_modal=id, temp= data)
        
        if not validar_digitosDecimales(temMax):
            flash('Por favor ingrese una temperatura valida valida', 'danger')
            return render_template('invernaderos/list_cultivos.html', temMaxErrEdit=True, edit_modal=id, temp= data)
        
        
        if not validar_espacios(cul):
            flash('Por favor ingrese un cultivo válido','danger')
            return redirect(url_for('ListCultivo'))
        
        if not validar_digitosDecimales(temMin):
            flash('Por favor ingrese un cultivo válido','danger')
            return redirect(url_for('ListCultivo'))
        
        if not validar_digitosDecimales(temMax):
            flash('Por favor ingrese un cultivo válido','danger')
            return redirect(url_for('ListCultivo'))
        
        
        # Verificar si no se han realizado cambios
        if repe['cultivo'] == cul and repe['temp_min'] == float(temMin) and repe['temp_max'] == float(temMax):
            flash('Cultivo sin cambios detectados', 'success')
            return redirect(url_for('ListCultivo'))
        
        # Si se está actualizando el nombre del cultivo, verificar si ya existe
        if repe['cultivo'] != cul:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM cultivos WHERE cultivo = %s', (cul,))
            existing_cultivo = cur.fetchone()
            cur.close()
            
            if existing_cultivo:
                flash(f'El cultivo {cul} ya existe en la base de datos', 'danger')
                return render_template('invernaderos/list_cultivos.html', dupliErrEdit=True, edit_modal=id, temp= data)
        
        # Actualizar las temperaturas del cultivo
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE cultivos
            SET cultivo = %s,
                temp_min = %s,
                temp_max = %s
    
            WHERE idcultivos = %s
        """, (cul,temMin, temMax, id))
        mysql.connection.commit()
        cur.close()
        flash('Cultivo actualizado exitosamente', 'success')
        return redirect(url_for('ListCultivo'))
#Eliminar
@app.route('/deleteCultivo/<string:id>', methods = ['POST','GET'])
def deleteCultivo(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM cultivos WHERE idcultivos = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Cultivo eliminado exitosamente', 'success')
        return redirect(url_for('ListCultivo'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el cultivo porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el cultivo: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListCultivo'))
#Agregar
@app.route('/add-cult', methods=["POST","GET"])
def addCultivo():
    cul = request.form['txtCulti']
    temMin = request.form['txtTempMin']
    temMax = request.form['txtTempMax']
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select cultivo from cultivos where cultivo = %s',(cul,))
    busquedaCC = cur.fetchone()
    cur.execute('SELECT idcultivos, cultivo, temp_min, temp_max ,CASE WHEN estado = 0 THEN \'Habilitado\' WHEN estado = 1 THEN \'Deshabilitado\' END AS status FROM cultivos')
    data = cur.fetchall()
    cur.close()
    
    
    if not validar_espacios(cul):
        flash('Por favor ingrese un cultivo valido', 'danger')
        return render_template('invernaderos/list_cultivos.html', culErr=True, add_modal=True, temp= data, cul=cul, temMin=temMin, temMax= temMax)
    
    if not validar_digitosDecimales(temMin):
        flash('Por favor ingrese una temperatura valida valida', 'danger')
        return render_template('invernaderos/list_cultivos.html', temMinErr=True, add_modal=True, temp= data, cul=cul, temMin=temMin, temMax= temMax)
    
    if not validar_digitosDecimales(temMax):
        flash('Por favor ingrese una temperatura valida valida', 'danger')
        return render_template('invernaderos/list_cultivos.html', temMaxErr=True, add_modal=True, temp= data, cul=cul, temMin=temMin, temMax= temMax)
    
    if  busquedaCC: 
        flash(f'El cultivo {cul} ya se encuentra creado', 'danger')
        return render_template('invernaderos/list_cultivos.html', dupliErr=True, add_modal=True, temp= data, cul=cul, temMin=temMin, temMax= temMax)
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
#Inhabilitar
@app.route('/InhabilCultivo/<string:id>', methods = ['POST','GET'])
def InhaCultivo(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update cultivos  set estado = 1 WHERE idcultivos = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Cultivo inhabilitado exitosamente', 'success')
        return redirect(url_for('ListCultivo'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede inhabilitar el Cultivo porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al inhabilitar el cliente: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListCultivo'))


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
    #print(request.form)
    if request.method == 'POST':
        nam1 = request.form['txtName1']
        nam2= request.form['txtName2']
        ape1= request.form['txtAp1']
        ape2 = request.form['txtAp2']
        cc = request.form['txtCc']
        tel = request.form['txtTel']
        mail = request.form['txtMail']
        tipe_str = request.form['tipoPersona']
        #state = request.form['state']
        
        cur=mysql.connection.cursor()
        cur.execute(""" select 
                c.idclientes, c.nombre_1, c.nombre_2, c.apellido_1, c.apellido_2, 
                c.cedula, c.telefono, c.correo, tc.tipo, Case when c.estado = 0 then 'Habilitado' When c.estado = 1 then 'Deshabilitado' 
                End as status
                from clientes c
                inner join tipo_clientes tc on c.tipo_cliente = tc.idtipo_clientes""")
        data = cur.fetchall()
        #cur = mysql.connection.cursor()
        cur.execute("""SELECT nombre_1, nombre_2, apellido_1, apellido_2, cedula, tipo_cliente, telefono, correo, estado
                    FROM clientes WHERE idclientes = %s""", (id,))
        repe = cur.fetchone()
        cur.execute('SELECT idtipo_clientes, tipo FROM tipo_clientes ')
        dataOpt = cur.fetchall()
        cur.close()
        
        if tipe_str:
            try:
                tipe = int(tipe_str)
            except ValueError:
                flash('Por favor, ingrese un tipo de cliente válido', 'danger')
                return render_template('tipo_cliente/clientes.html', client=data, allErr=True,dataOpt=dataOpt, edit_modal=id)
        else:
            flash('Por favor, seleccione un tipo de cliente', 'danger')
            return render_template('tipo_cliente/clientes.html', client=data, allErr=True,dataOpt=dataOpt, edit_modal=id)
        
        if not validar_cc(cc):
            flash('La cédula ingresada no es valida', 'danger')
            return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, ccErr=True, edit_modal=id,
            cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
        
        if not validar_nombre(nam1):
            flash('El nombre ingresado no es valido', 'danger')
            return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, nam1Err=True, edit_modal=id,
            cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
            #return redirect(url_for('ListClient'))
        
        if nam2 != '':
            if not validar_nombre(nam2):
                flash('El segundo nombre ingresado no es valido', 'danger')
                return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, nam2Err=True, edit_modal=id,
            cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
                #return redirect(url_for('ListClient'))
            
        if not validar_nombre(ape1):
            flash('El apellido ingresado no es valido', 'danger')
            return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, ape1Err=True, edit_modal=id,
            cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
            #return redirect(url_for('ListClient'))
        
        if nam2 != '':
            if not validar_nombre(ape2):
                flash('El segundo apellido ingresado no es valido', 'danger')
                return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, ape2Err=True, edit_modal=id,
                cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail )
                #return redirect(url_for('ListClient'))
            
        if not validar_celular(tel):
            flash('El celular ingresado no es valido', 'danger')
            return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, telErr=True, edit_modal=id,
            cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
            #return redirect(url_for('ListClient'))
        
        if not validar_correo(mail):
            flash('El correo inrgesado es incorrecto', 'danger')
            return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, mailErr=True, edit_modal=id,
            cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
            #return redirect(url_for('ListClient'))
        
        if nam1 == '' or ape1 == "" or cc == '' or tel == '' or mail =='' or tipe =='':
            flash('Por favor ingrese un cliente valido', 'danger')
            return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, allErr=True, edit_modal=id)
            #return redirect(url_for('ListClient'))
        
        if (repe['nombre_1'] == nam1 and repe['nombre_2'] == nam2 and repe['apellido_1'] == ape1 and repe['apellido_2'] == ape2 and 
            repe['cedula'] == cc and repe['tipo_cliente'] == tipe and repe['telefono'] == tel and repe['correo'] == mail ):
            flash('No hay cambios detectados', 'success')
            return redirect(url_for('ListClient'))
        
        if repe['cedula'] != cc:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM clientes WHERE cedula = %s', (cc,))
            existe = cur.fetchone()
            cur.close()
            
            if existe:
                flash(f'Hay un cliente con la cedula {cc} en la base de datos', 'danger')
                return render_template('tipo_cliente/clientes.html',client = data, dupliErr=True,dataOpt=dataOpt, edit_modal=id)
        
    
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
                tipo_cliente = %s
                
            WHERE idclientes= %s
        """, (nam1,nam2,ape1,ape2,cc,tel,mail,tipe,  id))
        mysql.connection.commit()
        cur.close()
        flash('Cliente actualizado exitosamente', 'success')
        return redirect(url_for('ListClient'))
#Elimnar
@app.route('/deleteCliente/<string:id>', methods = ['POST','GET'])
def deleteCliente(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM clientes WHERE idclientes = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Cliente eliminado exitosamente', 'success')
        return redirect(url_for('ListClient'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el cliente porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el cliente: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
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
    #print(cc)
    cur=mysql.connection.cursor()
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
    
    if not validar_cc(cc):
        flash('La cédula ingresada no es valida', 'danger')
        return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, ccErr=True, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
    
    if not validar_nombre(nam1):
        flash('El nombre ingresado no es valido', 'danger')
        return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, nam1Err=True, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
        #return redirect(url_for('ListClient'))
    
    if nam2 != '':
        if not validar_nombre(nam2):
            flash('El segundo nombre ingresado no es valido', 'danger')
            return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, nam2Err=True, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
            #return redirect(url_for('ListClient'))
        
    if not validar_nombre(ape1):
        flash('El apellido ingresado no es valido', 'danger')
        return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, ape1Err=True, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
        #return redirect(url_for('ListClient'))
    
    if nam2 != '':
        if not validar_nombre(ape2):
            flash('El segundo apellido ingresado no es valido', 'danger')
            return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, ape2Err=True, add_modal=True,
            cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail )
            #return redirect(url_for('ListClient'))
        
    if not validar_celular(tel):
        flash('El celular ingresado no es valido', 'danger')
        return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, telErr=True, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
        #return redirect(url_for('ListClient'))
    
    if not validar_correo(mail):
        flash('El correo inrgesado es incorrecto', 'danger')
        return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, mailErr=True, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
        #return redirect(url_for('ListClient'))
    
    if nam1 == '' or ape1 == "" or cc == '' or tel == '' or mail =='' or tipe =='':
        flash('Por favor ingrese un cliente valido', 'danger')
        return render_template('tipo_cliente/clientes.html',client = data, dataOpt=dataOpt, allErr=True, add_modal=True, 
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
        #return redirect(url_for('ListClient'))
    
    if not cc =='':
        cur = mysql.connection.cursor()
        cur.execute('Select cedula from clientes where cedula = {0}'.format(cc))
        busquedaCC = cur.fetchone()
        cur.close()
    
    
    if  busquedaCC: 
        flash(f'El cliente con cédula {cc} ya se encuentra creado', 'danger')
        #return redirect(url_for('ListClient'))
        return render_template('tipo_cliente/clientes.html',client = data, dupliErr=True,dataOpt=dataOpt, add_modal=True,
        cc=cc,nam1=nam1,nam2=nam2,ape1=ape1,ape2=ape2, tel=tel, mail=mail)
    else:

        try:
            cur = mysql.connection.cursor()
            #cur.execute("INSERT INTO clientes (nombre_1, nombre_2,)values(%s,%s)",(nam1, nam2))
            cur.execute("INSERT INTO clientes (nombre_1, nombre_2, apellido_1, apellido_2, cedula, telefono, correo, tipo_cliente, estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (nam1,nam2,ape1,ape2,cc,tel,mail,tipe,state))
            mysql.connection.commit()
            cur.close()
            flash('Cliente agregado con exito', 'success')
            return redirect(url_for('ListClient'))
        except mysql.connector.Error as e:
            if e.errno == 1451:
                flash('No se puede eliminar el cliente porque está relacionado con otros registros.', 'danger')
            else:
                flash('Error al agregar el cliente: {}'.format(str(e)), 'danger')
            
            return redirect(url_for('ListClient'))
#Inhabilitar
@app.route('/InhabilCliente/<string:id>', methods = ['POST','GET'])
def InhaCliente(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update clientes  set estado = 1 WHERE idclientes = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Cliente inhabilitado exitosamente', 'success')
        return redirect(url_for('ListClient'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el cliente porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el cliente: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListClient'))


#Metodos para dispositivos
#listar
@app.route('/listar-dispositivos')
def ListDispo():
    cur=mysql.connection.cursor()
    
    cur.execute(""" select
                d.iddispositivo, d.nombre, ac.accesorios, ar.arduino, tm.tipo_motor, ti.iluminacion,
                Case when d.estado = 0 then 'Habilitado' When d.estado = 1 then 'Deshabilitado'
                End as status
                from dispositivos d
                inner join tipo_arduino ar on ar.idarduinos = d.idarduino
                inner join tipo_sensor ac on ac.idaccesorios = d.idaccesorio
                inner join prueba.tipo_motor tm on d.idmotor = tm.idtipo_motor
                inner join tipo_iluminacion ti on ti.idtipo_iluminacion = d.idiluminacion""")
    data = cur.fetchall()
    
    cur.execute('SELECT idarduinos, arduino FROM tipo_arduino ')
    dataOpt = cur.fetchall()
    cur.execute('SELECT idaccesorios, accesorios FROM tipo_sensor ')
    dataOpt2 = cur.fetchall()
    cur.execute('SELECT idtipo_motor, tipo_motor FROM tipo_motor ')
    dataOpt3 = cur.fetchall()
    cur.execute('SELECT idtipo_iluminacion, iluminacion FROM tipo_iluminacion ')
    dataOpt4 = cur.fetchall()
    
    
    cur.close()
    return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4= dataOpt4)
#Agregar
@app.route('/add-dispo', methods=["POST","GET"])
def addDispo():
    #print(request.form)
    disp = request.form['txtDispo']
    acce= request.form['accesorio']
    ardui= request.form['arduino']
    state = request.form['state']
    mot = request.form['motor']
    ilum= request.form['iluminacion']
    #print(nam1)
    cur = mysql.connection.cursor()
    cur.execute('Select * from dispositivos where nombre = %s',(disp,))
    busquedaCC = cur.fetchone()
    cur.execute(""" select
                d.iddispositivo, d.nombre, ac.accesorios, ar.arduino, tm.tipo_motor, ti.iluminacion,
                Case when d.estado = 0 then 'Habilitado' When d.estado = 1 then 'Deshabilitado'
                End as status
                from dispositivos d
                inner join tipo_arduino ar on ar.idarduinos = d.idarduino
                inner join tipo_sensor ac on ac.idaccesorios = d.idaccesorio
                inner join prueba.tipo_motor tm on d.idmotor = tm.idtipo_motor
                inner join tipo_iluminacion ti on ti.idtipo_iluminacion = d.idiluminacion""")
    data = cur.fetchall()
    
    cur.execute('SELECT idarduinos, arduino FROM tipo_arduino ')
    dataOpt = cur.fetchall()
    cur.execute('SELECT idaccesorios, accesorios FROM tipo_sensor ')
    dataOpt2 = cur.fetchall()
    cur.execute('SELECT idtipo_motor, tipo_motor FROM tipo_motor ')
    dataOpt3 = cur.fetchall()
    cur.execute('SELECT idtipo_iluminacion, iluminacion FROM tipo_iluminacion ')
    dataOpt4 = cur.fetchall()
    cur.close()
    
    if not validar_espacios(disp):
        flash('El dispositivo ingresado no es valido', 'danger')
        return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4, dispErr=True, add_modal=True,
        disp= disp)
        
    if acce == '':
        flash('Por favor ingrese un accesorio', 'danger')
        return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4,accErr=True, add_modal=True,
        disp= disp)
        
    if ardui == '':
        flash('Por favor ingrese un arduino', 'danger')
        return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4,arduiErr=True, add_modal=True,
        disp= disp)
        
    if mot == '':
        flash('Por favor ingrese un motor', 'danger')
        return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4,motorErr=True, add_modal=True,
        disp= disp)
        
    if ilum == '':
        flash('Por favor ingrese una iluminación', 'danger')
        return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4,motorErr=True, add_modal=True,
        disp= disp)
        
    
    if  busquedaCC: 
        flash(f'El dispositivo {disp} ya se encuentra creado', 'danger')
        return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4,dupliErr=True, add_modal=True,
        disp= disp) 
    else:
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO dispositivos (nombre, idaccesorio,idarduino,idmotor,idiluminacion,estado)values(%s,%s,%s,%s,%s,%s)",(disp,acce,ardui,mot,ilum,state))
            mysql.connection.commit()
            cur.close()
            flash('Dispositivo agregado con exito', 'success')
            return redirect(url_for('ListDispo'))
        except Exception as e:
            flash('Error al agregar el dispositivo: {}'.format(str(e)), 'warning')
            return redirect(url_for('ListDispo'))
#Actualizar
@app.route('/updateDispo/<id>', methods=['POST'])
def updateDispo(id):
    #print(request.form)
    if request.method == 'POST':
        disp = request.form['txtDispo']
        acce= request.form['accesorio']
        ardui= request.form['arduino']
        mot= request.form['motor']
        ilum= request.form['iluminacion']
        #state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute("""select *  from dispositivos WHERE iddispositivo = %s""", (id,))
        repe = cur.fetchone()
        cur.execute(""" select
                d.iddispositivo, d.nombre, ac.accesorios, ar.arduino, tm.tipo_motor, ti.iluminacion,
                Case when d.estado = 0 then 'Habilitado' When d.estado = 1 then 'Deshabilitado'
                End as status
                from dispositivos d
                inner join tipo_arduino ar on ar.idarduinos = d.idarduino
                inner join tipo_sensor ac on ac.idaccesorios = d.idaccesorio
                inner join prueba.tipo_motor tm on d.idmotor = tm.idtipo_motor
                inner join tipo_iluminacion ti on ti.idtipo_iluminacion = d.idiluminacion""")
        data = cur.fetchall()
        
        cur.execute('SELECT idarduinos, arduino FROM tipo_arduino ')
        dataOpt = cur.fetchall()
        cur.execute('SELECT idaccesorios, accesorios FROM tipo_sensor ')
        dataOpt2 = cur.fetchall()
        cur.execute('SELECT idtipo_motor, tipo_motor FROM tipo_motor ')
        dataOpt3 = cur.fetchall()
        cur.execute('SELECT idtipo_iluminacion, iluminacion FROM tipo_iluminacion ')
        dataOpt4 = cur.fetchall()
        cur.close()
        
        if not validar_espacios(disp):
            flash('El dispositivo ingresado no es valido', 'danger')
            return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4,dispErrEdit=True, edit_modal=id)
            
        if acce == '':
            flash('Por favor ingrese un accesorio', 'danger')
            return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4,accErrEdit=True, edit_modal=id)
            
        if ardui == '':
            flash('Por favor ingrese un arduino', 'danger')
            return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4,arduiErrEdit=True, edit_modal=id)
        
        if mot == '':
            flash('Por favor ingrese un motor', 'danger')
            return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4,motorErr=True, edit_modal=id)
        
        if repe['nombre'] != disp:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM dispositivos WHERE nombre = %s', (disp,))
            existe = cur.fetchone()
            cur.close()
            
            if existe:
                flash(f'El dispositivo {disp} ya se encuentra creado', 'danger')
                return render_template('dispositivos/list_dispo.html', dispo = data, dataOpt=dataOpt, dataOpt2= dataOpt2, dataOpt3=dataOpt3, dataOpt4=dataOpt4, dupliErrEdit=True, edit_modal=id) 
        
        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE dispositivos
            SET nombre = %s,
                idaccesorio = %s,
                idarduino = %s,
                idmotor = %s,
                idiluminacion =%s
            
            WHERE iddispositivo= %s
        """, (disp,acce,ardui,mot,ilum, id))
        mysql.connection.commit()
        cur.close()
        flash('Dispositivo actualizado exitosamente', 'success')
        return redirect(url_for('ListDispo'))
#Elimnar
@app.route('/deleteDispo/<string:id>', methods = ['POST','GET'])
def deleteDispo(id): 
    cur=mysql.connection.cursor()
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM dispositivos WHERE iddispositivo = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Dispositivo eliminado exitosamente', 'success')
        return redirect(url_for('ListDispo'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el dispositivo porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el dispositivo: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListDispo'))
#Inhabilitar
@app.route('/InhabilDispo/<string:id>', methods = ['POST','GET'])
def InhaDispo(id):
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update dispositivos  set estado = 1 WHERE iddispositivo = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('El dispositivo se ha inhabilitado exitosamente', 'success')
        return redirect(url_for('ListDispo'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede inhabilitar el dispositivo porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al inhabilitar el dispositivo: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListDispo'))

#Metodos para tipo_invernadero
#Listar
@app.route('/listar-tipInve')
def ListTipInve():
    cur=mysql.connection.cursor()

    cur.execute("""SELECT idtipo_invernadero, tipo_invernadero,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_invernadero""")
    data = cur.fetchall()

    cur.close()
    return render_template('invernaderos/list_tipoInvernadero.html', tip = data)
#Agregar
@app.route('/add-tipInv', methods=["POST","GET"])
def addTipInve():
    tip = request.form['txtTip']
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select tipo_invernadero from tipo_invernadero where tipo_invernadero = %s',(tip,))
    busquedaCC = cur.fetchone()
    cur.execute("""SELECT idtipo_invernadero, tipo_invernadero,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_invernadero""")
    data = cur.fetchall()
    cur.close()
    
    if not validar_espacios(tip):
        flash('Por favor ingrese un tipo invernadero válido', 'danger')
        return render_template('invernaderos/list_tipoInvernadero.html', tipErr=True, add_modal=True, tip= data, tipe=tip)
    
    if  busquedaCC: 
        flash(f'El tipo de invernadero {tip} ya se encuentra creado', 'danger')
        return render_template('invernaderos/list_tipoInvernadero.html', dupliErr=True, add_modal=True, tip= data, tipe=tip)
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tipo_invernadero (tipo_invernadero, estado) VALUES (%s, %s)", (tip, state))
            mysql.connection.commit()
            flash('Tipo de invernadero agregado con exito', 'success')
            return redirect(url_for('ListTipInve'))
        except Exception as e:

            return 
#Eliminar
@app.route('/deleteTipInv/<string:id>', methods = ['POST','GET'])
def deleteTipInv(id): 
    cur=mysql.connection.cursor()
    
    try:
        cur.execute('DELETE FROM tipo_invernadero WHERE idtipo_invernadero = {0}'.format(id))
        mysql.connection.commit()
        flash('Tipo de invernadero eliminado exitosamente')
        return redirect(url_for('ListTipInve'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el tipo de invernadero porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el tipo de invernadero: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListTipInve'))
#Actualizar
@app.route('/updateTipInv/<id>', methods=['POST'])
def updateTipInv(id):
    if request.method == 'POST':
        tip = request.form['txtTip']
        #state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select tipo_invernadero from tipo_invernadero where tipo_invernadero = %s',(tip,))
        busquedaCC = cur.fetchone()
        cur.execute('Select tipo_invernadero from tipo_invernadero where idtipo_invernadero = %s',(id,))
        repe = cur.fetchone()
        cur.execute("""SELECT idtipo_invernadero, tipo_invernadero,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_invernadero""")
        data = cur.fetchall()
        cur.close()
    
        if not validar_espacios(tip):
            flash('Por favor ingrese un tipo invernadero válido', 'danger')
            return render_template('invernaderos/list_tipoInvernadero.html', tipErr=True, add_modal=True, tip= data, tipe=tip)
        
        if  tip == '':
            flash('Por favor ingrese un tipo invernadero válido', 'danger')
            return render_template('invernaderos/list_tipoInvernadero.html', tipErr=True, add_modal=True, tip= data, tipe=tip)
        
        if busquedaCC:
            if repe['tipo_invernadero'] == tip:
                flash('Tipo de invernadero sin cambios detectados', 'success')
                return redirect(url_for('ListTipInve'))
            elif busquedaCC['tipo_invernadero']:
                flash(f'El tipo de invernadero {tip} ya se encuentra creado', 'danger')
                return render_template('invernaderos/list_tipoInvernadero.html', dupliErr=True, add_modal=True, tip= data, tipe=tip)     
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE tipo_invernadero
                SET tipo_invernadero = %s
                    
                WHERE idtipo_invernadero= %s
            """, (tip,  id))
        mysql.connection.commit()
        flash('Tipo invernadero actualizado exitosamente','success')
        return redirect(url_for('ListTipInve'))
#Inhabilitar
@app.route('/InhabilTipInv/<string:id>', methods = ['POST','GET'])
def InhaTipInv(id):
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update tipo_invernadero  set estado = 1 WHERE idtipo_invernadero = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Tipo Invernadero inhabilitado exitosamente', 'success')
        return redirect(url_for('ListTipInve'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede inhabilitar el tipo invernadero porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al inhabilitar el tipo de invernadero: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListTipInve'))


#Metodos para tipo_iluminacion
#listar
@app.route('/listar-tipIlum')
def ListTipIlum():
    cur=mysql.connection.cursor()

    cur.execute("""SELECT idtipo_iluminacion, iluminacion,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_iluminacion""")
    data = cur.fetchall()

    cur.close()
    return render_template('iluminacion/list_iluminacion.html', tip = data)
#Agregar
@app.route('/add-tipIlum', methods=["POST","GET"])
def addTipIlum():
    tip = request.form['txtTip']
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select iluminacion from tipo_iluminacion where iluminacion = %s',(tip,))
    busquedaCC = cur.fetchone()
    cur.execute("""SELECT idtipo_iluminacion, iluminacion,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_iluminacion""")
    data = cur.fetchall()
    cur.close()
    
    if not validar_espacios(tip):
        flash('Por favor ingrese un tipo de iluminación válido', 'danger')
        return render_template('iluminacion/list_iluminacion.html', tipErr=True, add_modal=True, tip= data, tipe=tip)
    
    if  busquedaCC: 
        flash(f'El tipo de iluminación {tip} ya se encuentra creado', 'danger')
        return render_template('iluminacion/list_iluminacion.html', dupliErr=True, add_modal=True, tip= data, tipe=tip)
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tipo_invernadero (tipo_invernadero, estado) VALUES (%s, %s)", (tip, state))
            mysql.connection.commit()
            flash('Tipo de iluminación agregado con exito', 'success')
            return redirect(url_for('ListTipIlum'))
        except Exception as e:

            return 
#Eliminar
@app.route('/deleteTipIlum/<string:id>', methods = ['POST','GET'])
def deleteTipIlum(id): 
    cur=mysql.connection.cursor()
    
    try:
        cur.execute('DELETE FROM tipo_iluminacion WHERE idtipo_iluminacion = {0}'.format(id))
        mysql.connection.commit()
        flash('Tipo de iluminación eliminado exitosamente')
        return redirect(url_for('ListTipIlum'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el tipo de iluminación porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el tipo de iluminación: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListTipIlum'))
#Actualizar
@app.route('/updateTipIlum/<id>', methods=['POST'])
def updateTipIlum(id):
    if request.method == 'POST':
        tip = request.form['txtTip']
        #state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select iluminacion from tipo_iluminacion where idtipo_iluminacion = %s',(tip,))
        busquedaCC = cur.fetchone()
        cur.execute('Select iluminacion from tipo_iluminacion where idtipo_iluminacion = %s',(id,))
        repe = cur.fetchone()
        cur.execute("""SELECT idtipo_iluminacion, iluminacion,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM tipo_iluminacion""")
        data = cur.fetchall()
        cur.close()
    
        if not validar_espacios(tip):
            flash('Por favor ingrese un tipo de iluminación válido', 'danger')
            return render_template('iluminacion/list_iluminacion.html', tipErr=True, add_modal=True, tip= data, tipe=tip)
        
        if  tip == '':
            flash('Por favor ingrese un tipo iluminación válido', 'danger')
            return render_template('iluminacion/list_iluminacion.html', tipErr=True, add_modal=True, tip= data, tipe=tip)
        
        if busquedaCC:
            if repe['tipo_invernadero'] == tip:
                flash('Tipo de iluminación sin cambios detectados', 'success')
                return redirect(url_for('ListTipInve'))
            elif busquedaCC['tipo_invernadero']:
                flash(f'El tipo de iluminación {tip} ya se encuentra creado', 'danger')
                return render_template('iluminacion/list_iluminacion.html', dupliErr=True, add_modal=True, tip= data, tipe=tip)     
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE tipo_iluminacion
                SET iluminacion = %s
                    
                WHERE idtipo_iluminacion= %s
            """, (tip,  id))
        mysql.connection.commit()
        flash('Tipo de iluminación actualizado exitosamente','success')
        return redirect(url_for('ListTipIlum'))
#Inhabilitar
@app.route('/InhabilTipIlum/<string:id>', methods = ['POST','GET'])
def InhaTipIlum(id):
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update tipo_iluminacion  set estado = 1 WHERE idtipo_iluminacion = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Tipo de iluminación inhabilitado exitosamente', 'success')
        return redirect(url_for('ListTipIlum'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede inhabilitar el tipo de iluminación porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al inhabilitar el tipo de iluminación: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListTipIlum'))



#Metodos para invernaderos
#listar
@app.route('/listar-invernaderos')
def ListInverna():
    cur=mysql.connection.cursor()
    
    cur.execute(""" SELECT idinvernaderos, nombre_invernadero, c.cultivo, ti.tamanio,
                    d.nombre, c2.cedula, ti2.tipo_invernadero,
                    Case when i.estado = 0 then 'Habilitado' When i.estado = 1 then 'Deshabilitado'
                                End as status
                from invernaderos i
                inner join cultivos c on i.idCultivo = c.idcultivos
                inner join clientes c2 on i.idcliente = c2.idClientes
                inner join dispositivos d on i.iddispositivo = d.iddispositivo
                inner join tamanios_invernadero ti on i.idtamanio = ti.idtamanios
                inner join tipo_invernadero ti2 on i.tipo_invernadero = ti2.idtipo_invernadero""")
    data = cur.fetchall()
    
    cur.execute('SELECT idcultivos, cultivo FROM cultivos ')
    dataOpt = cur.fetchall()
    cur.execute('SELECT idclientes, cedula FROM clientes ')
    dataOpt2 = cur.fetchall()
    cur.execute('SELECT iddispositivo, nombre FROM dispositivos ')
    dataOpt3 = cur.fetchall()
    cur.execute('SELECT idtamanios, tamanio FROM tamanios_invernadero ')
    dataOpt4 = cur.fetchall()
    cur.execute('SELECT idtipo_invernadero, tipo_invernadero FROM tipo_invernadero ')
    dataOpt5 = cur.fetchall()
    
    cur.close()
    return render_template('invernaderos/list_invernaderos.html', dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
#Agregar
@app.route('/add-inverna', methods=["POST","GET"])
def addInverna():
    #print(request.form)
    inve = request.form['txtInve']
    cc_str= request.form['cedula']
    cult_str= request.form['cultivo']
    dispo_str = request.form['Dispositivo']
    tip_str = request.form['tipo']
    tam_str = request.form['tamanio']
    state = request.form['state']
    #print(nam1)
    cur = mysql.connection.cursor()
    cur.execute('Select * from invernaderos where nombre_invernadero = %s',(inve,))
    busquedaCC = cur.fetchone()
    cur.execute(""" SELECT idinvernaderos, nombre_invernadero, c.cultivo, ti.tamanio,
                    d.nombre, c2.cedula, ti2.tipo_invernadero,
                    Case when i.estado = 0 then 'Habilitado' When i.estado = 1 then 'Deshabilitado'
                                End as status
                from invernaderos i
                inner join cultivos c on i.idCultivo = c.idcultivos
                inner join clientes c2 on i.idcliente = c2.idClientes
                inner join dispositivos d on i.iddispositivo = d.iddispositivo
                inner join tamanios_invernadero ti on i.idtamanio = ti.idtamanios
                inner join tipo_invernadero ti2 on i.tipo_invernadero = ti2.idtipo_invernadero""")
    data = cur.fetchall()
    
    cur.execute('SELECT idcultivos, cultivo FROM cultivos ')
    dataOpt = cur.fetchall()
    cur.execute('SELECT idclientes, cedula FROM clientes ')
    dataOpt2 = cur.fetchall()
    cur.execute('SELECT iddispositivo, nombre FROM dispositivos ')
    dataOpt3 = cur.fetchall()
    cur.execute('SELECT idtamanios, tamanio FROM tamanios_invernadero ')
    dataOpt4 = cur.fetchall()
    cur.execute('SELECT idtipo_invernadero, tipo_invernadero FROM tipo_invernadero ')
    dataOpt5 = cur.fetchall()
    cur.close()
    
    if not validar_espacios(inve):
        flash('Por favor ingrese un invernadero valido', 'danger')
        return render_template('invernaderos/list_invernaderos.html', add_modal=True, inveErr=True, inve=inve, dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    
    if cc_str:
        try:
                cc = int(cc_str)
        except ValueError:
                flash('Por favor, ingrese un cliente válido', 'danger')
                return render_template('invernaderos/list_invernaderos.html', cc=cc,add_modal=True, ccErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    else:
            flash('Por favor, ingrese un cliente válido', 'danger')
            return render_template('invernaderos/list_invernaderos.html',  add_modal=True, ccErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    if cult_str:
        try:
                cult = int(cult_str)
        except ValueError:
                flash('Por favor, ingrese un cultivo válido', 'danger')
                return render_template('invernaderos/list_invernaderos.html',  add_modal=True, cultErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    else:
            flash('Por favor, ingrese un cultivo válido', 'danger')
            return render_template('invernaderos/list_invernaderos.html',  add_modal=True, cultErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    if dispo_str:
        try:
                dispo = int(dispo_str)
        except ValueError:
                flash('Por favor, ingrese un dispositivo válido', 'danger')
                return render_template('invernaderos/list_invernaderos.html',  add_modal=True, dispoErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    else:
            flash('Por favor, ingrese un dispositivo válido', 'danger')
            return render_template('invernaderos/list_invernaderos.html',  add_modal=True, dispoErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    if tip_str:
        try:
                tip = int(tip_str)
        except ValueError:
                flash('Por favor, ingrese un tipo de invernadero válido', 'danger')
                return render_template('invernaderos/list_invernaderos.html',  add_modal=True, tipErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    else:
            flash('Por favor, ingrese un tipo de invernadero válido', 'danger')
            return render_template('invernaderos/list_invernaderos.html',  add_modal=True, tipErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    if tam_str:
        try:
                tam = int(tam_str)
        except ValueError:
                flash('Por favor, ingrese un tamaño válido', 'danger')
                return render_template('invernaderos/list_invernaderos.html',  add_modal=True, tamErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    else:
            flash('Por favor, ingrese un tamaño válido', 'danger')
            return render_template('invernaderos/list_invernaderos.html',  add_modal=True, tamErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)     
            
            
    if cc =='' or cult =='' or dispo =='' or tip =='' or tam=='' or state =='':
        flash('Por favor ingrese un invernadero valido', 'danger')
        return render_template('invernaderos/list_invernaderos.html', add_modal=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)    
    
    if  busquedaCC: 
        flash(f'El invernadero {inve} ya se encuentra creado', 'danger')
        return render_template('invernaderos/list_invernaderos.html', add_modal=True, dupliErr=True, dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
    else:
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO invernaderos (nombre_invernadero, idCultivo, idtamanio, iddispositivo, idcliente, tipo_invernadero, estado)values(%s,%s,%s,%s,%s,%s,%s)",
                        (inve,cult,tam,dispo,cc,tip,state))
            mysql.connection.commit()
            cur.close()
            flash('Invernadero agregado con exito', 'success')
            return redirect(url_for('ListInverna'))
        except Exception as e:
            flash('Error al agregar el dispositivo: {}'.format(str(e)), 'danger')
            return redirect(url_for('ListInverna'))
#Actualizar
@app.route('/updateInverna/<id>', methods=['POST'])
def updateInverna(id):
    #print(request.form)
    if request.method == 'POST':
        inve = request.form['txtInve']
        cc_str= request.form['cedula']
        cult_str= request.form['cultivo']
        dispo_str = request.form['Dispositivo']
        tip_str = request.form['tipo']
        tam_str = request.form['tamanio']
        #state = request.form['state']
        
        
        cur = mysql.connection.cursor()
        cur.execute(""" SELECT idinvernaderos, nombre_invernadero, c.cultivo, ti.tamanio,
                    d.nombre, c2.cedula, ti2.tipo_invernadero,
                    Case when i.estado = 0 then 'Habilitado' When i.estado = 1 then 'Deshabilitado'
                                End as status
                from invernaderos i
                inner join cultivos c on i.idCultivo = c.idcultivos
                inner join clientes c2 on i.idcliente = c2.idClientes
                inner join dispositivos d on i.iddispositivo = d.iddispositivo
                inner join tamanios_invernadero ti on i.idtamanio = ti.idtamanios
                inner join tipo_invernadero ti2 on i.tipo_invernadero = ti2.idtipo_invernadero""")
        data = cur.fetchall()
        cur.execute("""select *  from invernaderos WHERE idinvernaderos = %s""", (id,))
        repe = cur.fetchone()
        cur.execute('SELECT idcultivos, cultivo FROM cultivos ')
        dataOpt = cur.fetchall()
        cur.execute('SELECT idclientes, cedula FROM clientes ')
        dataOpt2 = cur.fetchall()
        cur.execute('SELECT iddispositivo, nombre FROM dispositivos ')
        dataOpt3 = cur.fetchall()
        cur.execute('SELECT idtamanios, tamanio FROM tamanios_invernadero ')
        dataOpt4 = cur.fetchall()
        cur.execute('SELECT idtipo_invernadero, tipo_invernadero FROM tipo_invernadero ')
        dataOpt5 = cur.fetchall()
        cur.close()

        if not validar_espacios(inve):
            flash('Por favor ingrese un invernadero valido', 'danger')
            return render_template('invernaderos/list_invernaderos.html', edit_modal=id, inveErr=True, inve=inve, dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        
        if cc_str:
            try:
                    cc = int(cc_str)
            except ValueError:
                    flash('Por favor, ingrese un cliente válido', 'danger')
                    return render_template('invernaderos/list_invernaderos.html', cc=cc,edit_modal=id, ccErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        else:
                flash('Por favor, ingrese un cliente válido', 'danger')
                return render_template('invernaderos/list_invernaderos.html',  edit_modal=id, ccErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        if cult_str:
            try:
                    cult = int(cult_str)
            except ValueError:
                    flash('Por favor, ingrese un cultivo válido', 'danger')
                    return render_template('invernaderos/list_invernaderos.html',  edit_modal=id, cultErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        else:
                flash('Por favor, ingrese un cultivo válido', 'danger')
                return render_template('invernaderos/list_invernaderos.html',  edit_modal=id, cultErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        if dispo_str:
            try:
                    dispo = int(dispo_str)
            except ValueError:
                    flash('Por favor, ingrese un dispositivo válido', 'danger')
                    return render_template('invernaderos/list_invernaderos.html',  edit_modal=id, dispoErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        else:
                flash('Por favor, ingrese un dispositivo válido', 'danger')
                return render_template('invernaderos/list_invernaderos.html',  edit_modal=id, dispoErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        if tip_str:
            try:
                    tip = int(tip_str)
            except ValueError:
                    flash('Por favor, ingrese un tipo de invernadero válido', 'danger')
                    return render_template('invernaderos/list_invernaderos.html',  edit_modal=id, tipErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        else:
                flash('Por favor, ingrese un tipo de invernadero válido', 'danger')
                return render_template('invernaderos/list_invernaderos.html',  edit_modal=id, tipErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        if tam_str:
            try:
                    tam = int(tam_str)
            except ValueError:
                    flash('Por favor, ingrese un tamaño válido', 'danger')
                    return render_template('invernaderos/list_invernaderos.html',  edit_modal=id, tamErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        else:
                flash('Por favor, ingrese un tamaño válido', 'danger')
                return render_template('invernaderos/list_invernaderos.html',  edit_modal=id, tamErr=True,dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                            dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)
        
        
        if cc =='' or cult =='' or dispo =='' or tip =='' or tam=='':
            flash('Por favor ingrese un invernadero valido', 'danger')
            return redirect(url_for('ListInverna'))
        
        if not validar_espacios(inve):
            flash('Por favor ingrese un invernadero valido', 'danger')
            return redirect(url_for('ListInverna'))
        
        if repe['nombre_invernadero'] != inve:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM invernaderos WHERE nombre_invernadero = %s', (inve,))
            existe = cur.fetchone()
            cur.close()
            
            if existe:
                flash(f'El invernadero {inve} ya se encuentra creado', 'danger')
                return render_template('invernaderos/list_invernaderos.html', edit_modal=id, dupliErr=True, dispo = data, dataOpt= dataOpt, dataOpt2= dataOpt2,
                        dataOpt3 = dataOpt3, dataOpt4=dataOpt4, dataOpt5=dataOpt5)

        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE invernadero
            SET nombre_invernadero = %s,
                idCultivo = %s,
                idtamanio = %s,
                iddispositivo = %s,
                idcliente = %s,
                tipo_invernadero = %s
                
            WHERE idinvernaderos= %s
        """, (inve,cult,tam,dispo,cc,tip,  id))
        mysql.connection.commit()
        cur.close()
        flash('Invernadero actualizado exitosamente', 'success')
        return redirect(url_for('ListDispo'))
#Elimnar
@app.route('/deleteInverna/<string:id>', methods = ['POST','GET'])
def deleteInverna(id): 
    cur=mysql.connection.cursor()
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM invernaderos WHERE idinvernaderos = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Invernadero eliminado exitosamente', 'success')
        return redirect(url_for('ListInverna'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el invernadero porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al eliminar el dispositivo: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListInverna'))
#Inhabilitar
@app.route('/InhabilInverna/<string:id>', methods = ['POST','GET'])
def InhaInverna(id): 
    try:
        cur=mysql.connection.cursor()
        cur.execute('Update invernaderos  set estado = 1 WHERE idinvernaderos = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Invernadero inhabilitado exitosamente', 'success')
        return redirect(url_for('ListInverna'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede inhabilitar el invernadero porque está relacionado con otros registros.', 'warning')
        else:
            flash('Error al inhabilitar el invernadero: {}'.format(str(e)), 'warning')
    finally:
        cur.close()
    return redirect(url_for('ListInverna'))


#Metodo para temperatura
#listar
@app.route('/listar-temp')
def ListTemp():
    cur=mysql.connection.cursor()
    
    cur.execute("""select
                    dt.iddatos_temperaturas,
                    dt.datos_temperaturas,
                    dt.fecha_temperatura,
                    d.nombre,
                    Case when dt.estado = 0 then 'Habilitado' When dt.estado = 1 then 'Deshabilitado'
                                End as status
                    from datos_temperaturas dt
    inner join dispositivos d on d.iddispositivo = dt.iddispositivo""")
    data = cur.fetchall()
    
    
    cur.close()
    return render_template('temperaturas/temperaturas.html', temp = data)








def validar_correo(correo):
    patron_correo = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron_correo, correo)

def validar_celular(celular):
    patron_celular = r'^\d{1,10}$'
    return re.match(patron_celular, celular)

def validar_usuario(usuario):
    patron_usuario = r'^[a-zA-Z0-9_-]{3,16}$'
    return re.match(patron_usuario, usuario)

def validar_nombre(nombre):
    patron_nombre = r'^[a-zA-Z\s]{3,}(?:\s[a-zA-Z]+)*$'
    return re.match(patron_nombre, nombre)

def validar_espacios(value):
    patron_espacios = r'^[a-zA-Z0-9_-]+(\s[a-zA-Z0-9_-]+)*\S$'
    return re.match(patron_espacios,value)

def validar_digitosDecimales(value):
    patron_digitos = r'^\d{1,4}(\.\d{1,2})?$'
    return re.match(patron_digitos, value)

def validar_cc(value):
    patron_cedula = r'^\d{7,10}$'
    return re.match(patron_cedula, value)





if __name__ == '__main__':
    app.secret_key="projectoU"
    app.run(debug=True,host='0.0.0.0', port=3000, threaded=True)