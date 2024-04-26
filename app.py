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
    
    cur = mysql.connection.cursor()
    cur.execute('Select name from usuarios where name = %s',(correo,))
    busquedaCC = cur.fetchone()
    cur.close()
    
    if  busquedaCC: 
        #flash(f'El usuario {correo} ya se encuentra creado', 'danger')
        return render_template('Login_register/registro.html', registerWrong= f'El usuario {correo} ya se encuentra creado')
    
    
    if not validar_usuario(correo):
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
        
        cur = mysql.connection.cursor()
        cur.execute('Select name from usuarios where name = %s',(name,))
        busquedaCC = cur.fetchone()
        cur.execute('Select name from usuarios where id = %s',(id,))
        repe = cur.fetchone()
        cur.close()
    
        
        
        if  password == '' or name ==  '':
            flash('Por favor inrgese un usuario valido','danger')
            return redirect(url_for('ListUser'))
        
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
            flash('No se puede eliminar el usuario porque está relacionado con otros registros.', 'danger')
        else:
            flash('Error al eliminar el usuario: {}'.format(str(e)), 'danger')
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
    cur = mysql.connection.cursor()
    correo = request.form['txtCorreo']
    password = request.form['txtPassword']
    perfil_id = request.form['perfil']
    #print(request.form)
    
    cur = mysql.connection.cursor()
    cur.execute('Select name from usuarios where name = %s',(correo,))
    busquedaCC = cur.fetchone()
    cur.close()
    
    if  busquedaCC: 
        flash(f'El usuario {correo} ya se encuentra creado', 'danger')
        return redirect(url_for('ListUser')) 
    
    if not validar_usuario(correo):
        flash('El usuario ingresado no es valido valido','danger')
        return redirect(url_for('ListUser')) 
    
    if  password == '' or perfil_id =='':
        flash('Por favor inrgese un usuario valido','danger')
        return redirect(url_for('ListUser'))
    
    else:
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (name, password, idperfil) VALUES (%s, %s, %s)", (correo, password, perfil_id))
            mysql.connection.commit()
            cur.close()
            flash('Usuario agregado con exito', 'success')
            return redirect(url_for('ListUser'))
        except Exception as e:
            flash('Error al agregar un usuario', 'danger')
            print(e)
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
        state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select perfiles from perfiles where perfiles = %s',(perfil,))
        busquedaCC = cur.fetchone()
        cur.execute('Select perfiles from perfiles where idperfiles = %s',(id,))
        repe = cur.fetchone()
        cur.close()
    
        
        
        if  perfil == '':
            flash('Por favor ingrese un perfil valido','danger')
            return redirect(url_for('ListPerfil'))
        
        if busquedaCC:
            if repe['perfiles'] == perfil:
                flash('Perfil sin cambios detectados', 'success')
                return redirect(url_for('ListPerfil'))
            elif busquedaCC['perfiles']:
                flash(f'El perfil {perfil} ya se encuentra creado', 'danger')
                return redirect(url_for('ListPerfil'))  
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
    
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM perfiles WHERE idperfiles = {0}'.format(id))
        mysql.connection.commit()
        flash('Perfil eliminado exitosamente','success')
        return redirect(url_for('ListPerfil'))
    except Exception  as e:
            if '1451' in str(e):
                flash('No se puede eliminar el perfil porque está relacionado con otros registros.', 'danger')
            else:
                flash('Error al eliminar el perfil: {}'.format(str(e)), 'danger')
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
    cur.close()
    
    
    if not validar_nombre(perfil):
        flash('Por favor ingrese un perfil valido', 'danger')
        return redirect(url_for('ListPerfil'))
    
    
    if  busquedaCC: 
        flash(f'El perfil {perfil} ya se encuentra creado', 'danger')
        return redirect(url_for('ListPerfil'))     

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

#Metodos para accesorios
#Listar
@app.route('/listar-acce')
def ListAcce():
    cur=mysql.connection.cursor()

    cur.execute("""SELECT idaccesorios,accesorios,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM accesorios""")
    data = cur.fetchall()

    cur.close()
    return render_template('accesorios/list_acce.html', acce = data)
#Actualizar
@app.route('/updateAcce/<id>', methods=['POST'])
def updateAcce(id):
    if request.method == 'POST':
        acce = request.form['txtAcce']
        state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select accesorios from accesorios where accesorios = %s',(acce,))
        busquedaCC = cur.fetchone()
        cur.execute('Select accesorios from accesorios where idaccesorios = %s',(id,))
        repe = cur.fetchone()
        cur.close()
    
        
        
        if  acce == '':
            flash('Por favor inrgese un accesorio valido','danger')
            return redirect(url_for('ListAcce'))
        
        if busquedaCC:
            if repe['accesorios'] == acce:
                flash('Accesorio sin cambios detectados', 'success')
                return redirect(url_for('ListAcce'))
            elif busquedaCC['*']:
                flash(f'El accesorio {acce} ya se encuentra creado', 'danger')
                return redirect(url_for('ListAcce'))   

        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE accesorios
                SET accesorios = %s,
                    estado = %s
                WHERE idaccesorios = %s
            """, (acce, state,  id))
        mysql.connection.commit()
        flash('Accesorio actualizado exitosamente','success')
        return redirect(url_for('ListAcce'))
#Eliminar
@app.route('/deleteAcce/<string:id>', methods = ['POST','GET'])
def deleteAcce(id): 
    
    try:
        cur=mysql.connection.cursor()   
        cur.execute('DELETE FROM accesorios WHERE idaccesorios = {0}'.format(id))
        mysql.connection.commit()
        flash('Accesorio eliminado exitosamente')
        return redirect(url_for('ListAcce'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el accesorio porque está relacionado con otros registros.', 'danger')
        else:
            flash('Error al eliminar el accesorio: {}'.format(str(e)), 'danger')
    finally:
        cur.close()
    return redirect(url_for('ListAcce'))
#Agregar
@app.route('/add-acce', methods=["POST","GET"])
def addAcce():
    acce = request.form['txtAcce']
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select accesorios from accesorios where accesorios = %s',(acce,))
    busquedaCC = cur.fetchone()
    cur.close()
    
    if not validar_espacios(acce):
        flash('Por favor ingrese un accesorio valido','danger')
        return redirect(url_for('ListAcce'))
        
    if  busquedaCC: 
        flash(f'El accesorio {acce} ya se encuentra creado', 'danger')
        return redirect(url_for('ListAcce')) 
    else:

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO accesorios (accesorios, estado) VALUES (%s, %s)", (acce, state))
            mysql.connection.commit()
            flash('Accesorio agregado con exito')
            return redirect(url_for('ListAcce'))
        except Exception as e:
            flash(f'Error al agregar el accesorio{e}')
            return 


#Metodos para arduinos
#Listar
@app.route('/listar-ard')
def ListArd():
    cur=mysql.connection.cursor()

    cur.execute("""SELECT idarduinos,arduino,
                    Case when estado = 0 then 'Habilitado' When estado = 1 then 'Deshabilitado' 
                    End as status
                    FROM arduinos""")
    data = cur.fetchall()

    cur.close()
    return render_template('arduinos/list_arduino.html', ard = data)
#Actualizar
@app.route('/updateArd/<id>', methods=['POST'])
def updateArd(id):
    if request.method == 'POST':
        ard = request.form['txtArd']
        state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select arduino from arduinos where arduino = %s',(ard,))
        busquedaCC = cur.fetchone()
        cur.execute('Select arduino from arduinos where idarduinos = %s',(id,))
        repe = cur.fetchone()
        cur.close()
        
        if  ard == '':
            flash('Por favor ingrese un arduino valido','danger')
            return redirect(url_for('ListArd'))
        
        if busquedaCC:
            if repe['arduino'] == ard:
                flash('Arduino sin cambios detectados', 'success')
                return redirect(url_for('ListArd'))
            elif busquedaCC['arduino']:
                flash(f'El arduino {ard} ya se encuentra creado', 'danger')
                return redirect(url_for('ListArd'))     

        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE arduinos
                SET arduino = %s,
                    estado = %s
                WHERE idarduinos= %s
            """, (ard, state,  id))
        mysql.connection.commit()
        flash('Arduino actualizado exitosamente','success')
        return redirect(url_for('ListArd'))
#Eliminar
@app.route('/deleteArd/<string:id>', methods = ['POST','GET'])
def deleteArd(id): 
    
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM arduinos WHERE idarduinos = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Arduino eliminado exitosamente','success')
        return redirect(url_for('ListArd'))
    
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el arduino porque está relacionado con otros registros.', 'danger')
        else:
            flash('Error al eliminar el arduino: {}'.format(str(e)), 'danger')
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
    cur.close()
    
    if not validar_espacios(ard):
        flash('Por favor ingrese una arduino valido','danger')
        return redirect(url_for('ListArd'))
    
    if  busquedaCC: 
        flash(f'El arduino {ard} ya se encuentra creado', 'danger')
        return redirect(url_for('ListArd')) 
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
        state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('Select tipo from tipo_clientes where tipo = %s',(tip,))
        busquedaCC = cur.fetchone()
        cur.execute('Select tipo from tipo_clientes where idtipo_clientes = %s',(id,))
        repe = cur.fetchone()
        cur.close()
    
        if not validar_espacios(tip):
            flash('Por favor ingrese un tipo cliente valido','danger')
            return redirect(url_for('ListTipClient'))
        
        if  tip == '':
            flash('Por favor ingrese un tipo cliente valido','danger')
            return redirect(url_for('ListTipClient'))
        
        if busquedaCC:
            if repe['tipo'] == tip:
                flash('Tipo cliente sin cambios detectados', 'success')
                return redirect(url_for('ListTipClient'))
            elif busquedaCC['tipo']:
                flash(f'El tipo cliente {tip} ya se encuentra creado', 'danger')
                return redirect(url_for('ListTipClient'))      
        else:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE tipo_clientes
                SET tipo = %s,
                    estado = %s
                WHERE idtipo_clientes= %s
            """, (tip, state,  id))
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
            flash('No se puede eliminar el tipo cliente porque está relacionado con otros registros.', 'danger')
        else:
            flash('Error al eliminar el tipo cliente: {}'.format(str(e)), 'danger')
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
    cur.close()
    
    if not validar_espacios(tip):
        flash('Por favor ingrese un tipo cliente valido', 'danger')
        return redirect(url_for('ListTipClient'))
    
    if  busquedaCC: 
        flash(f'El tipo cliente {tip} ya se encuentra creado', 'danger')
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
        
        cur = mysql.connection.cursor()
        cur.execute('Select tamanio from tamanios_invernadero where tamanio = %s',(tam,))
        busquedaCC = cur.fetchone()
        cur.execute('Select tamanio from tamanios_invernadero where idtamanios = %s',(id,))
        repe = cur.fetchone()
        cur.close()
    
        if not validar_digitosDecimales(tam):
            flash('Por favor ingrese un tamaño valido','danger')
            return redirect(url_for('ListTamanio'))
        
        if  tam == '':
            flash('Por favor ingrese un tamaño valido','danger')
            return redirect(url_for('ListTamanio'))
        
        if busquedaCC:
            if repe['tamanio'] == tam:
                flash('Tamaño sin cambios detectados', 'success')
                return redirect(url_for('ListTamanio'))
            elif busquedaCC['tamanio']:
                flash(f'El la medida {tam} metros ya se encuentra creado', 'danger')
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
    try:
        cur.execute('DELETE FROM tamanios_invernadero WHERE idtamanios = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Tamaño eliminado exitosamente', 'success')
        return redirect(url_for('ListTamanio'))    
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar la medida porque está relacionado con otros registros.', 'danger')
        else:
            flash('Error al eliminar la medida: {}'.format(str(e)), 'danger')
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
    cur.close()
    
    if not validar_digitosDecimales(tam):
        flash('Por favor ingrese un tamaño valido', 'danger')
        return redirect(url_for('ListTamanio'))
    
    if  busquedaCC: 
        flash(f'El la medida {tam} metros ya se encuentra creada', 'danger')
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
        temMin = float(request.form['txtTempMin'])
        temMax = float(request.form['txtTempMax'])
        state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT cultivo, temp_min, temp_max FROM cultivos WHERE idcultivos = %s', (id,))
        repe = cur.fetchone()
        
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
        if repe['cultivo'] == cul and repe['temp_min'] == temMin and repe['temp_max'] == temMax:
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
                return redirect(url_for('ListCultivo'))
        
        # Actualizar las temperaturas del cultivo
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE cultivos
            SET cultivo = %s,
                temp_min = %s,
                temp_max = %s,
                estado = %s
            WHERE idcultivos = %s
        """, (cul,temMin, temMax, state, id))
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
            flash('No se puede eliminar el cultivo porque está relacionado con otros registros.', 'danger')
        else:
            flash('Error al eliminar el cultivo: {}'.format(str(e)), 'danger')
    finally:
        cur.close()
    return redirect(url_for('ListCultivo'))
#Agregar
@app.route('/add-cult', methods=["POST","GET"])
def addCultivo():
    cul = request.form['txtCulti']
    temMin = float(request.form['txtTempMin'])
    temMax = float(request.form['txtTempMax'])
    state = request.form['state']
    
    cur = mysql.connection.cursor()
    cur.execute('Select cultivo from cultivos where cultivo = %s',(cul,))
    busquedaCC = cur.fetchone()
    cur.close()
    
    if not validar_espacios(cul):
        flash('Por favor inrgese un cultivo valido', 'danger')
        return redirect(url_for('ListCultivo'))
    
    if not validar_digitosDecimales(temMin):
        flash('Por favor inrgese un cultivo valido', 'danger')
        return redirect(url_for('ListCultivo'))
    
    if not validar_digitosDecimales(temMax):
        flash('Por favor inrgese un cultivo valido', 'danger')
        return redirect(url_for('ListCultivo'))
    
    if  busquedaCC: 
        flash(f'El cultivo {cul} ya se encuentra creado', 'danger')
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
    #print(request.form)
    if request.method == 'POST':
        nam1 = request.form['txtName1']
        nam2= request.form['txtName2']
        ape1= request.form['txtAp1']
        ape2 = request.form['txtAp2']
        cc = request.form['txtCc']
        tel = request.form['txtTel']
        mail = request.form['txtMail']
        tipe = int(request.form['tipoPersona'])
        state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute("""SELECT nombre_1, nombre_2, apellido_1, apellido_2, cedula, tipo_cliente, telefono, correo, estado
                    FROM clientes WHERE idclientes = %s""", (id,))
        repe = cur.fetchone()
        
        if not validar_nombre(nam1):
            flash('El nombre ingresado no es valido', 'danger')
            return redirect(url_for('ListClient'))
        if nam2 != '':
            if not validar_nombre(nam2):
                flash('El segundo nombre ingresado no es valido', 'danger')
                return redirect(url_for('ListClient'))
        
        if not validar_nombre(ape1):
            flash('El apellido ingresado no es valido', 'danger')
            return redirect(url_for('ListClient'))
        if nam2 != '':
            if not validar_nombre(nam2):
                flash('El segundo nombre ingresado no es valido', 'danger')
                return redirect(url_for('ListClient'))
            
        if not validar_celular(tel):
            flash('El celular ingresado no es valido', 'danger')
            return redirect(url_for('ListClient'))
        
        if not validar_correo(mail):
            flash('El correo inrgesado es incorrecto', 'danger')
            return redirect(url_for('ListClient'))
        
        if not validar_cc(cc):
            flash('La cédula ingresada es incorrecta', 'danger')
            return redirect(url_for('ListClient'))
        
        if (repe['nombre_1'] == nam1 and repe['nombre_2'] == nam2 and repe['apellido_1'] == ape1 and repe['apellido_2'] == ape2 and 
            repe['cedula'] == cc and repe['tipo_cliente'] == tipe and repe['telefono'] == tel and repe['correo'] == mail and repe['estado'] == state):
            flash('No hay cambios detectados', 'success')
            return redirect(url_for('ListClient'))
        
        if repe['cedula'] != cc:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM clientes WHERE cedula = %s', (cc,))
            existe = cur.fetchone()
            cur.close()
            
            if existe:
                flash(f'Hay un cliente con la cedula {cc} en la base de datos', 'danger')
                return redirect(url_for('ListClient'))
        
    
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
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM clientes WHERE idclientes = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Cliente eliminado exitosamente', 'success')
        return redirect(url_for('ListClient'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el cliente porque está relacionado con otros registros.', 'danger')
        else:
            flash('Error al eliminar el cliente: {}'.format(str(e)), 'danger')
    finally:
        cur.close()
    return redirect(url_for('ListClient'))


    if not validar_espacios(tip):
        flash('Por favor ingrese un * valido', 'danger')
        return redirect(url_for('*'))
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
    
    if not validar_nombre(nam1):
        flash('El nombre ingresado no es valido', 'danger')
        return redirect(url_for('ListClient'))
    
    if nam2 != '':
        if not validar_nombre(nam2):
            flash('El segundo nombre ingresado no es valido', 'danger')
            return redirect(url_for('ListClient'))
        
    if not validar_nombre(ape1):
        flash('El apellido ingresado no es valido', 'danger')
        return redirect(url_for('ListClient'))
    
    if nam2 != '':
        if not validar_nombre(nam2):
            flash('El segundo nombre ingresado no es valido', 'danger')
            return redirect(url_for('ListClient'))
        
    if not validar_celular(tel):
        flash('El celular ingresado no es valido', 'danger')
        return redirect(url_for('ListClient'))
    
    if not validar_correo(mail):
        flash('El correo inrgesado es incorrecto', 'danger')
        return redirect(url_for('ListClient'))
    
    if nam1 == '' or ape1 == "" or cc == '' or tel == '' or mail =='' or tipe =='':
        flash('Por favor ingrese un cliente valido', 'danger')
        return redirect(url_for('ListClient'))
    
    if not cc =='':
        cur = mysql.connection.cursor()
        cur.execute('Select cedula from clientes where cedula = {0}'.format(cc))
        busquedaCC = cur.fetchone()
        cur.close()
    
    
    if  busquedaCC: 
        flash(f'El cliente con cédula {cc} ya se encuentra creado', 'danger')
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
        except mysql.connector.Error as e:
            if e.errno == 1451:
                flash('No se puede eliminar el cliente porque está relacionado con otros registros.', 'danger')
            else:
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
    cur = mysql.connection.cursor()
    cur.execute('Select * from dispositivos where nombre = %s',(disp,))
    busquedaCC = cur.fetchone()
    cur.close()
    
    if not validar_espacios(disp):
        flash('Por favor ingrese un dispositivo valido', 'danger')
        return redirect(url_for('ListDispo'))
    
    if  busquedaCC: 
        flash(f'El dispositivo {disp} ya se encuentra creado', 'danger')
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
    #print(request.form)
    if request.method == 'POST':
        disp = request.form['txtDispo']
        acce= request.form['accesorio']
        ardui= request.form['arduino']
        state = request.form['state']
        
        cur = mysql.connection.cursor()
        cur.execute("""select *  from dispositivos WHERE iddispositivo = %s""", (id,))
        repe = cur.fetchone()
        
        
        if acce == '' or ardui == '':
            flash('Por favor ingrese un dispositivo valido', 'danger')
            return redirect(url_for('ListDispo'))
        
        if not validar_espacios(disp):
            flash('Por favor ingrese un dispositivo valido', 'danger')
            return redirect(url_for('ListDispo'))
        
        if repe['nombre'] != disp:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM dispositivos WHERE nombre = %s', (disp,))
            existe = cur.fetchone()
            cur.close()
            
            if existe:
                flash(f'El dispositivo {disp} ya se encuentra creado', 'danger')
                return redirect(url_for('ListDispo'))
        
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
    try:
        cur=mysql.connection.cursor()
        cur.execute('DELETE FROM dispositivos WHERE iddispositivo = {0}'.format(id))
        mysql.connection.commit()
        cur.close()
        flash('Dispositivo eliminado exitosamente', 'success')
        return redirect(url_for('ListDispo'))
    except Exception  as e:
        if '1451' in str(e):
            flash('No se puede eliminar el dispositivo porque está relacionado con otros registros.', 'danger')
        else:
            flash('Error al eliminar el dispositivo: {}'.format(str(e)), 'danger')
    finally:
        cur.close()
    return redirect(url_for('ListDispo'))


    if not validar_espacios(tip):
        flash('Por favor ingrese un * valido', 'danger')
        return redirect(url_for('*'))

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
    patron_nombre = r'^[a-zA-Z\s]+$'
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