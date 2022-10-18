#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__)



@app.route("/")
def home():  
	print(dato2) 	
	return render_template("Inicio.html")

if __name__ == "__main__":
    #app.run()
    app.run(host='0.0.0.0', port=5000, debug=True)
