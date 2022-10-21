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
  cotizacion_txt = cotizacion.text.strip()

  # Se crea un fichero auxiliar para añadir el dato de cotización
  fich2 = open("fich2.html","a")
  fich2.write(now)
  fich2.write(cotizacion_txt)
  fich2.write(" || ")
  fich2.close()

  # Se muestra el dato y fecha actuales
  print("-----------------------------")
  print(now + cotizacion_txt)
  print("-----------------------------")

  # Se programa la ejecución en segundo plano de la función cada 2 minutos 
  threading.Timer(120, ext_cotizacion).start()




@app.route("/")
# """
#   Página principal de la app
# """
def home(nombre=None):

  if 'email' in session:
    return render_template("inicio2.html", nombre=session['user'])  
  
  else:  
    ext_cotizacion()
    return render_template("inicio.html")   

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
def registersuccess(nombre=None): 

  if request.method == "POST":        
    session['email']=request.form['email']
    session['user'] = request.form['name']
    session['password'] = request.form['password'] 

    ###comprobar que no existe ya el correo almacenar en bbdd
    ###almacenar en bbd si no existe

    return render_template('inicio2.html', nombre=session['user'])  #...,usr = session['user'])

#------------------------------------------------------------------

@app.route('/salida') 
# """
#    Página de salida de la app
# """ 
def logout():

  #session.pop('email',None)  
  session.clear()
  return render_template('inicio.html');  

#------------------------------------------------------------------

if __name__ == "__main__":
    #app.run()
    app.run(host='0.0.0.0', port=5000, debug=True)
