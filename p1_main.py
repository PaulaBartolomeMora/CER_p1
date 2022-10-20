#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, request, session
app = Flask(__name__)

from bs4 import BeautifulSoup 
import os


@app.route("/")
# """
#   Página principal de la app
# """
def home():  

	#if primera vez que se accede a la app
		#se extrae el valor
		#se almacena 
		#se presenta print 


  # Se descarga a un fichero local el contenido de la web
  os.system("wget -O fich.html 'https://es.investing.com/currencies/eur-usd'")

  # Se abre el fichero para leerlo y formatear el html
  fich = open("fich.html").read()
  pretty = BeautifulSoup(fich).prettify()

  # Se "parsea" el contenido 
  bs = BeautifulSoup(pretty, 'lxml')

  # Se busca la etiqueta donde aparece el dato de la cotización
  span = bs.find('span', {'class',  "text-2xl"})

  # Se crea un fichero auxiliar para añadir el dato de cotización
  fich2 = open("fich2.html","a")
  fich2.write(span.text)
  fich2.close()

  # Se muestra el datoa actual
  print(span.text)

  	#return render_template("Inicio.html") #homepage2
  #else
  return render_template("Inicio.html") #homepage2 	


#------------------------------------------------------------------

@app.route('/entrada') 
# """
#    Página de entrada de la app
# """ 
def login():  

	if 'email' in session:
	    return render_template('Inicio.html') #homepage2 
	else:
	    return render_template('Entrada.html') #loginpage3


#------------------------------------------------------------------

@app.route('/entradabien',methods = ["POST"]) 
# """
#    Página de entrada satisfactoria a la app
# """
def success(): 

	if request.method == "POST": 				######## 
   		session['email']=request.form['email']
   		session['user'] = request.form['name']
   		session['pass'] = request.form['pass'] 
   		#session['peticiones'] = 0
   		return render_template('EntradaBien.html') #success3 	#...,usr = session['user'])

#------------------------------------------------------------------

@app.route('/salida') 
# """
#    Página de salida de la app
# """ 
def logout():

	if 'email' in session:  
		session.pop('email',None)  
		#session.clear()
		return render_template('Salida.html'); #logoutpage2

	else:  
		return '<p>El usuario ya ha salido</p>'   

#------------------------------------------------------------------

@app.route("/registro")
def register():
# """
#   	Página de registro de la app
# """ 
    if 'email' in session:
    	session.pop('email',None) 
        #session.clear()
    return render_template('Registro.html') #register

#------------------------------------------------------------------

if __name__ == "__main__":
    #app.run()
    app.run(host='0.0.0.0', port=5000, debug=True)
