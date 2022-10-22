#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, request, session
app = Flask(__name__)
app.secret_key = "ayush" 

from bs4 import BeautifulSoup 
from datetime import datetime 
import os, time, threading, uuid, hashlib 


#------------------------------------------------------------------


# Configuración de Redis 
import redis
from redis.exceptions import DataError, ConnectionError

# Intento de conexión a Redis
try:
  redis_client = redis.Redis(host='127.0.0.1', port='6379', db='0')
  redis_client.ping()
  print('-*-*-*-*-*-*-*-*Conectado a REDIS-*-*-*-*-*-*-*-*')

except ConnectionError:
  print('-*-*-*-*-*-*-*-*No se puede conectar a REDIS-*-*-*-*-*-*-*-*')


#------------------------------------------------------------------


def ext_cotizacion():

  # Se obtiene la hora y fecha actual
  now = datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')

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
  text = now + " " + cotizacion_text

  fich2.write(text)
  fich2.write(" || ")
  fich2.close()

  # Se muestra el dato y fecha actuales
  print("-----------------------------")
  print(text)
  print("-----------------------------")

  # Se inserta el dato de cotización y la fecha de extracción en la BBDD
  try:

    # Lista 1: se añade cotización + fecha actual 
    redis_client.rpush("lista_cot_fecha", text)

    # Lista 2: se añade cotización (para calcular la media y ver la evolución del histórico)
    redis_client.rpush("lista_cot", cotizacion_text)

    # Se calcula el nº total de cotizaciones almacenadas y se muestra el historial 
    n_cot = redis_client.llen("lista_cot")
    print(redis_client.lrange("lista_cot", 0, n_cot))

  except DataError:
    print('Error al insertar la cotizacion actual en la BBDD')

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
    session['email'] = request.form['email']
    session['password'] = request.form['password'] 

    lista_usuarios = redis_client.keys()
    print(lista_usuarios)

    try:
      # Antes de entrar se comprueba que el usuario introducido existe en la BBDD 
      if redis_client.exists(session['email']) == 1:
        return render_template('inicio2.html', nombre=session['email']) ########################

      else:
        print("El usuario introducido no existe")
        # Se pone invalid=1 para indicar en la web que el usuario no existe
        return render_template('entrada.html', invalid=1) 

    except DataError:
      print('Error al insertar el nuevo usuario en la BBDD')

    return render_template('inicio2.html', nombre=session['user'])  


#------------------------------------------------------------------


@app.route("/registro")
# """
#     Página de registro de la app
# """ 

def register():

  return render_template('registro.html', invalid=0) 


#------------------------------------------------------------------


@app.route('/registroOK', methods = ["POST"]) 
# """
#    Página de entrada satisfactoria a la app
# """

def registersuccess(nombre=None, email=None, password=None): 

  if request.method == "POST":     

    session['email'] = request.form['email']
    email_to_redis = session['email']

    session['user'] = request.form['name']
    user_to_redis = session['user']

    session['password'] = request.form['password'] 
    password_to_redis = session['password'] 

    # Se codifica la contraseña antes de almacenarla en la BBDD
    codif_password = hashlib.sha256(uuid.uuid4().hex.encode() + password_to_redis.encode()).hexdigest() + ':' + uuid.uuid4().hex
    
    lista_usuarios = redis_client.keys()
    print(lista_usuarios)

    try:
      # Antes de añadir el usuario y sus datos se comprueba que no existe ya en la BBDD 
      if redis_client.exists(email_to_redis) == 0:
        redis_client.hset(user_to_redis, mapping={"email": email_to_redis, "password": codif_password})
        print(redis_client.hgetall(user_to_redis))
        return render_template('inicio2.html', nombre=session['user'])

      else:
        print("No se puede registrar el usuario, ya existe")
        # Se pone invalid=1 para indicar en la web que el usuario ya existe
        return render_template('registro.html', invalid=1) 

    except DataError:
      print('Error al insertar el nuevo usuario en la BBDD')


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
    app.run(host='0.0.0.0', port=5000, debug=True)
