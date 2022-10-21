#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, request, session
app = Flask(__name__)
app.secret_key = "ayush" 

from bs4 import BeautifulSoup 
from datetime import datetime 
import os
import time
import threading

# Configuración de Redis 
from flask_redis import FlaskRedis 
from redis.exceptions import DataError, ConnectionError

# from flask_redis import FlaskRedis
# redis_client = FlaskRedis(app)

# Parámetros de redis (por defecto):
host = 'localhost'
port = 6379
db = 0
key = 'usuario' # clave bajo la que se almacenan los conjuntos de datos (dato:<nombre_dato>)

# Intento de conexión a Redis
try:
  redis_client = FlaskRedis(app)
  print(f'Conexión a REDIS en {host}:{port}')
  #redis_client = redis.Redis(host=host, port=port, db=db)

except ConnectionError:
  print(f'No se puede conectar a REDIS en {host}:{port}')
  print('Salida del sistema')
  sys.exit(1)


#------------------------------------------------------------------


def ext_cotizacion():

  # Se obtiene la hora y fecha actual
  now = datetime.now().strftime('[%d-%m-%Y %H:%M:%S] ')

  # Se descarga a un fichero local el contenido de la web
  os.system("wget -O fich.html 'https://es.investing.com/currencies/eur-usd'")

  # Se abre el fichero para leerlo y formatear el html
  fich = open("fich.html").read()
  pretty = BeautifulSoup(fich, 'lxml').prettify()

  # Se "parsea" el contenido 
  bs = BeautifulSoup(pretty, 'lxml')

  # Se busca el dato de la cotización en su etiqueta respectiva
  cotizacion = bs.find('span', {'class',  "text-2xl"})
  cotizacion_text = cotizacion.text.strip()

  # Se crea un fichero auxiliar para añadir el dato de cotización con su fecha
  fich2 = open("fich2.html","a")
  text = now + cotizacion_text

  fich2.write(text)
  fich2.write(" || ")
  fich2.close()

  # Se muestra el dato y fecha actuales
  print("-----------------------------")
  print(text)
  print("-----------------------------")

  # Se programa la ejecución en segundo plano de la función cada 2 minutos 
  threading.Timer(120, ext_cotizacion).start()

  return cotizacion_text


#------------------------------------------------------------------


@app.route("/")
# """
#   Página principal de la app
# """
def home(nombre=None, cot_actual=None):

  ext_cot = ext_cotizacion()

  if 'email' in session:
    return render_template("inicio2.html", nombre=session['user'])  
  
  else:  
    # Se obtiene la cotización para mostrarla la primera vez que se entra a la web
    return render_template("inicio.html", cot_actual=ext_cot)   


#------------------------------------------------------------------


@app.route('/entrada') 
 # """
 #    Página de entrada de la app
 # """ 
def login():  

  return render_template('entrada.html') 


#------------------------------------------------------------------


@app.route('/entradaOK', methods = ["POST"]) 
# """
#    Página de entrada satisfactoria a la app
# """
def entrysuccess(nombre=None): 

  if request.method == "POST":        
    session['email']=request.form['email']
    session['password'] = request.form['password'] 

    ######comprobar que sí existe ya el correo
    ##si no existe se manda a inicio.html

    ###buscar en la bbdd el nombre
    #session['user'] = 

    return render_template('inicio2.html', nombre=session['user'])  


#------------------------------------------------------------------


@app.route("/registro")
# """
#     Página de registro de la app
# """ 
def register():
  return render_template('registro.html') 


#------------------------------------------------------------------


@app.route('/registroOK', methods = ["POST"]) 
# """
#    Página de entrada satisfactoria a la app
# """
def registersuccess(nombre=None, email=None, password=None): 

  if request.method == "POST":        
    session['email']=request.form['email']
    email_to_redis = session['email']

    session['user'] = request.form['name']
    user_to_redis = session['user']

    session['password'] = request.form['password'] 
    password_to_redis = session['password'] 

    ###comprobar que no existe ya el correo almacenar en bbdd
    ###almacenar en bbd si no existe

    try:
      zset = f'{key}:{user_to_redis}'
      datos = {email: email_to_redis, password: password_to_redis}
      redis_client.zadd(zset, datos)
      print(f'Datos: {email, password} almacenados en la BBDD para el usuario: {zset}')
        
    except DataError:
      print('Error al insertar en base de datos')

    return render_template('inicio2.html', nombre=session['user']) 


#------------------------------------------------------------------


@app.route('/salida') 
# """
#    Página de salida de la app
# """ 
def logout(cot_actual=None):

  #session.pop('email',None)  
  session.clear()
  return render_template('inicio.html', cot_actual=None); 


#------------------------------------------------------------------


if __name__ == "__main__":
    #app.run()
    app.run(host='0.0.0.0', port=5000, debug=True)
