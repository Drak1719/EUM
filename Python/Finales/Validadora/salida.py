#!/usr/bin/env python3
import time
import Botones as botones
#import RPi.GPIO as GPIO
import leerConfiguracionFechaHora as confFH
import configuracionEXP as archivoConfiguracion
import fechaUTC
import os
import os.path
import sys
import psycopg2
from pygame import mixer
import cliente as cliente
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtWidgets import QMainWindow,QApplication, QDialog, QGridLayout, QMessageBox,QLabel, QPushButton, QLineEdit,QSpinBox, QTableWidget,QTableWidgetItem,QComboBox,QCheckBox
from threading import Thread
import sys
#from escposprinter import *
from datetime import datetime, timedelta
from Conexiones.Conexiones import Conexiones
from Pila.Pila import Pila
import requests
import json

'''DL17'''
from encriptacionQR import codificar
'''DL17'''

sucursal_id = 4
conexion_activa = False

#GPIO.setmode(GPIO.BCM)
espera = 0
idSal = 0
reproduccion = 0
plaza = ""
localidad = ""
usuario = 'postgres'
contrasenia = 'Postgres3UMd6'
bd = "dbeum_tecamac"
rrr=0
red=59
green=109
blue=153
pantalla_cont = 0
iface=0
activa=True
camInicial=''
gerencia=False 
segundos = 0
contadorMensaje = 0
mensajePrincipal = ""
estado = 1

configuracion = []



leido = ""
validacion = ""
USUARIO=''
host=''
ip=''
noEquipo = 0
plaza = ""
localidad = ""
user="eum"
pswd="pi"
tolerancia=0
fechaIn	=fechaUTC.fechaConFormato()
horaEnt = fechaUTC.tiempoConFormato()
leyendaCandado = ""

#horaDeApagado=confFH.getHora()

class Ui_ventanaAcceso(QDialog):

	global gui,iface

	def __init__(self):		
		QDialog.__init__(self)
		iface=1
		gui = uic.loadUi("/home/cajero/Documentos/eum/app/salida/ventanas/rb.ui", self)
		self.stackedWidget.setCurrentIndex(0)
		self.leerBotones()
		self.mostrarIconoWifi()
		self.bapagar.clicked.connect(lambda:self.apagarRasp())
		self.breiniciar.clicked.connect(lambda:self.reiniciarRasp())
		#self.bcamara.clicked.connect(lambda:self.cam())
		self.balza.clicked.connect(self.alza)
		self.datosEstacionamiento()
		self.bcamara.clicked.connect(self.scan)
		#self.bcamara.setShortcut("Return")		
		self.lscan.textChanged.connect(self.validacionScan)
		
		################MODS########
		self.bapagar.clicked.connect(lambda:self.apagarRasp())
		self.breiniciar.clicked.connect(lambda:self.reiniciarRasp())
		self.bconfirmarIP.clicked.connect(self.cambiaIp)
		self.bpanelconf.clicked.connect(self.muestraPanel)
		self.bsalirConfig.clicked.connect(lambda:self.cambia(0))
		self.bsalirLogin.clicked.connect(lambda:self.cambia(0))
		self.bsalirsucursal.clicked.connect(lambda:self.cambia(4))
		self.bsalirred.clicked.connect(lambda:self.cambia(4))
		self.bsalirCambiarFecha.clicked.connect(lambda:self.cambia(4))
		self.bsucursal.clicked.connect(lambda:self.cambia(3))
		self.bred.clicked.connect(lambda:self.cambia(2))
		self.breporte.clicked.connect(lambda:self.cambia(0))
		self.bhora.clicked.connect(lambda:self.cambia(6))
		
		self.lerror1.setVisible(False)
		self.bentrar.clicked.connect(self.validaLogin)
		self.bcambiarFecha.clicked.connect(self.cambiaFecha)
		#self.bguardar.clicked.connect(self.setConfig)
		#self.bsalirConfig.clicked.connect(self.salirConf)
		self.bconfirmarplaza.clicked.connect(self.setConfig)
		self.panelConfig()
		self.datosEstacionamiento()
		self.contadorSegundos()
		
		
		
	def contadorSegundos(self):
		global segundos,contadorMensaje,mensajePrincipal
		if(contadorMensaje==1):
			segundos=segundos+1
			if(segundos==3): #3 MINUTOS TOLERANCIA
				v=0
				contadorMensajes=0
				self.avisoInserta.setText(mensajePrincipal)

		QtCore.QTimer.singleShot(1000,self.contadorSegundos)
		
		
	def mostrarIconoWifi(self):
		global conexion_activa
		try:
			if(conexion_activa):
				self.bwifi.setEnabled(True)
			else:
				self.bwifi.setEnabled(False)
		except:
			print("ocurrio un error")
		QtCore.QTimer.singleShot(5000, self.mostrarIconoWifi)
		
	
	def validaLogin(self):
		global cur,accesoAcaja,USUARIO,correoUSUARIO,user,pswd
		nom=self.lusu.text()
		rol_us=""
		indice=0
		contr=self.lcont.text()
		if(nom==user):
			if(contr==pswd):
				self.cambia(5)
			else:
				self.lerror1.setText("usuario o contraseña incorrectos")
				self.lerror1.setVisible(True)
		else:
			self.lerror1.setText("usuario o contraseña incorrectos")
			self.lerror1.setVisible(True)

	
	def cambiaFecha(self):
		a=self.dtime.dateTime()
		b=self.dtime.textFromDateTime(a)
		print(b,type(b))
		os.system("sudo date -s '"+b+"' ")
		
	def setConfig(self):
		global plaza,localidad,noEquipo,host,ip,pol,pol1,pol2,pol3,pol4,pol5,impresora,anchoPapel
		lenn=0
		plaza=str(self.lnom.text())
		localidad=str(self.lloc.text())
		noEquipo=str(self.leq.text())
		
		
		print(plaza,localidad)
		dat=plaza+","+localidad+","+str(noEquipo)
		infile = open("/home/cajero/Documentos/eum/app/salida/archivos_config/datos.txt", 'w')
		c=infile.write(dat)
		
		self.datosEstacionamiento()
		self.cambia(0)

		
	def datosEstacionamiento(self):
		global plaza,localidad,noEquipo,host,ip,pol,pol1,pol2,pol3,pol4,pol5,impresora,anchoPapel
		lenn=0
		self.lnom.setText(plaza)
		self.lloc.setText(localidad)
		self.leq.setText(str(noEquipo))
		self.nomPlaza.setText(plaza)
		self.nomLoc.setText(localidad)
		self.lhost.setText(host)
		self.lip.setText(ip)
		
		
	def panelConfig(self):
		global plaza,localidad,noEquipo,host,ip,sucursal_id
		infile = open('/home/cajero/Documentos/eum/app/salida/archivos_config/datos.txt','r')
		datos= infile.readline()
		arr=datos.split(',')
		plaza=arr[0]
		localidad=arr[1]
		noEquipo=arr[2]
		infile.close()
		
		infile = open('/home/cajero/Documentos/eum/app/salida/archivos_config/red.txt','r')
		datos= infile.readline()
		arr=datos.split(',')
		host=arr[0]
		ip=arr[1]
		infile.close()
		
		infile = open('/home/cajero/Documentos/eum/sys/sucursal.txt','r')
		datos= infile.readline()
		sucursal_id=datos
		infile.close()
		
		
	def salirConf(self):
		global panelConf
		panelConf=0
		self.cambia(1)
		

	
	
	
	def sustituye(self,archivo,buscar,reemplazar):
		"""

		Esta simple función cambia una linea entera de un archivo

		Tiene que recibir el nombre del archivo, la cadena de la linea entera a

		buscar, y la cadena a reemplazar si la linea coincide con buscar

		"""
		with open(archivo, "r") as f:

			# obtenemos las lineas del archivo en una lista

			lines = (line.rstrip() for line in f)
			print(lines)

	 

			# busca en cada linea si existe la cadena a buscar, y si la encuentra

			# la reemplaza

			

			altered_lines = [reemplazar if line==buscar else line for line in lines]
			f= open(archivo, "w+")
			print(altered_lines[0],len(altered_lines))
			for i in range(len(altered_lines)):
				if(buscar in altered_lines[i]):
					print (altered_lines[i])
					cambia=altered_lines[i]
					f.write(reemplazar+"\n")
				else:
					f.write(altered_lines[i]+"\n")
			f.close()
			
			
	def cambiaIp(self):
		global host,ip
		host=self.lhost.text()
		ip=self.lip.text()

		self.sustituye("/home/cajero/Documentos/eum/app/salida/cliente.py","192.168","host = '"+host+"'")
		self.sustituye("/etc/dhcpcd.conf","ip_address","static ip_address="+ip+"/24")
		ip=ip.split(".")
		ip=ip[0]+"."+ip[1]+"."+ip[2]+".1"
		self.sustituye("/etc/dhcpcd.conf","routers","static routers="+ip)

		
		host=str(self.lhost.text())
		ip=str(self.lip.text())
		
		
		print(plaza,localidad)
		dat=host+","+ip
		infile = open("/home/cajero/Documentos/eum/app/salida/archivos_config/red.txt", 'w')
		c=infile.write(dat)
		
		self.datosEstacionamiento()
		self.cambia(0)
		
		
	def muestraPanel(self):
		self.cambia(4)
		#datos=obtenerPlazaYLocalidad()
		#self.lno.setText(str(datos[0]))
		#self.llo.setText(str(datos[1]))
		#datos=obtenerTerminal()
		self.lusu.setText('')
		self.lcont.setText('')
		self.lerror1.setText('')
		
	def cambia(self,val):
		self.stackedWidget.setCurrentIndex(val)
		############################MODS FIN#################
	
	def validacionScan(self):
		global leido
		#thread3 = Thread(target=leerCodQR, args = ())
		try:
			text=str(self.lscan.text())		
			if( '.' in text ):
				'''DL17'''
				dencriptador = codificar()
				resultado = dencriptador.procesamiento(text)
				'''DL17'''
				inicioChar=resultado[:1]		
				if inicioChar == "C":
					if len(resultado) > 7:
						if("CHT" in resultado):
							leido = resultado
							self.lscan.setText('')
							print(resultado)
							#leerArch = open("datos.txt", "w")
							#leerArch.write(text)
							#leerArch.close()
						else:
							leido = resultado
							self.lscan.setText('')
						#else:
						#self.scan2()					
				if "." in resultado:
					inicioChar=resultado[:1]
					if inicioChar == "M":
						#text = text[1:-1:]
						self.scan(resultado)
					else:
						self.lscan.setText('')		
				#text2char=text[:2]
				#scan()
		except:
			print("Try again...")
			self.lscan.setText('')

	def scan2(self):
		global leido
		#thread3 = Thread(target=leerCodQR, args = ())
		text=self.lscan.text()
		
		text2char=text[:2]
		if('M,' == text2char or 'L,' == text2char):
			if 'M,' == text2char:
				text = text[0:-1:]   #Retira caracteres de inicio y de fin
			text=text.replace("'","-")
			text=text.replace("Ñ",":")
			text=text.split(',')
			#os.system("sudo nice -n -19 python3 archimp.py")
			#os.system("sudo nice -n -19 python3 archimp.py")
			try:
				leerArch = open("/home/cajero/Documentos/ticket.txt", "w")
				leerArch.write(str(text[0])+"\n"+str(text[1])+"\n"+str(text[2])+"\n"+str(text[3])+"\n"+str(text[4])[:8])
				leerArch.close()

				leido = text
				self.lscan.setText('')
			except Exception as e:
				print(e,'datetime incorrecto')
				self.lscan.setText('')
				pass
		else:
			mensajeBoletoUsado = 1
			self.lscan.setText('')
			print('boleto invalido',text,text2char)

	def scan(self, text):
		global leido
		#thread3 = Thread(target=leerCodQR, args = ())
		'''text=self.lscan.text()'''
		#text=self.lscan.text()
		
		text2char=text[:2]
		if('M,' == text2char or 'L,' == text2char):
			if 'M,' == text2char:
				text = text[0:-1:]   #Retira caracteres de inicio y de fin
			text=text.replace("'","-")
			text=text.replace("Ñ",":")
			text=text.split(',')
			print(text, file=open("textSplit.txt", "a"))
			#os.system("sudo nice -n -19 python3 archimp.py")
			#os.system("sudo nice -n -19 python3 archimp.py")
			try:
				print(str(text[3])+" "+str(text[4]),'datetime...')
				fecha = datetime.strptime(str(text[3])+" "+str(text[4]), '%d-%m-%Y %H:%M:%S')
				leerArch = open("/home/cajero/Documentos/ticket.txt", "w")
				leerArch.write(str(text[0])+"\n"+str(text[1])+"\n"+str(text[2])+"\n"+str(text[3])+"\n"+str(text[4])[:8])
				leerArch.close()
				textStr = ''
				for i in text:
					textStr = textStr + i + ","
				leido = textStr
				self.lscan.setText('')
				print('leido...',leido)
			except Exception as e:
				print(e,'datetime incorrecto')
				self.lscan.setText('')
				pass
		else:
			mensajeBoletoUsado = 1
			self.lscan.setText('')
			print('boleto invalido',text,text2char)	
		
	def scan3(self):
		global leido
		#thread3 = Thread(target=leerCodQR, args = ())
		text=self.lscan.text()
		text=text.replace("'","-")
		text=text.replace("Ñ",":")
		
		
		if("CHT" in text):
			leido = text
			self.lscan.setText('')
			print(text)
			#leerArch = open("datos.txt", "w")
			#leerArch.write(text)
			#leerArch.close()
			
		else:
			#os.system("sudo nice -n -19 python3 archimp.py")
			leido = text
			self.lscan.setText('')
			"""try:
				
				text=text.split(',')
				leerArch = open("datos.txt", "w")
				leerArch.write(str(text[0])+"\n"+str(text[1])+"\n"+str(text[2])+"\n"+str(text[3])+"\n"+str(text[4]))
				leerArch.close()
				self.lscan.setText('')
				print(text)
			except Exception as e:

				print(e,text)
				pass
			"""


	
	mensaje = 0

	f1 = f2 = f3 = f4 = f5 = f6 = f7 = False
	error = 0

	def alza(self):
		botones.configurarPinesGPIO()
		botones.configurarPinesGPIOBobina()
		botones.abrir()	

	def leerBotones(self):
		global leyendaCandado,espera,pantalla_cont,reproduccion,red,green,blue,rrr,iface,tolerancia,gerencia,sucursal_id, leido, validacion, estado
		
		if(red<50):
			rrr=1
		if(red>150):
			rrr=0
		if(rrr==0):
			red=red-20
			green=green-20
			blue=blue-20
		else:
			red=red+20
			green=green+20
			blue=blue+20
			
		self.lboleto.setStyleSheet("color:rgb("+str(red)+", "+str(green)+", "+str(blue)+");background-color:transparent;")
		
		self.fechaLabel()
		tiempo = 0
		if self.f1 != True:
			self.f2 = False
			print("------Presencia Auto --------")
			if(iface==1):
				iface=0
				self.apagarRasp()
			#self.apagarRasp()
			if pantalla_cont != 0:
				pantalla_cont = pantalla_cont + 1
				print(pantalla_cont)
				if pantalla_cont == 60:
					self.stackedWidget.setCurrentIndex(0)
					self.lboleto.setText("---> Inserte su boleto <---")
					pantalla_cont = 0
			#if botones.leerMasa() == 1:
			
			if "M," in leido:
				print("ticket leido:",leido)
				gerencia = False
				leido = leido.split(",")
				idBol = leido [1]
				idExp = leido [2]
				fecBol = leido [3]
				horBol = leido [4]
				fechaAMD=fecBol.split('-',2)
				fechaAMD=fechaAMD[2]+"-"+fechaAMD[1]+"-"+fechaAMD[0]
				print("exp:"+str(idExp) + " " + "idBol:"+str(idBol) + " " + "fec:"+fechaAMD + " " + "horaBol:"+horBol)
				fechaConc = str(fechaAMD)+ " " + str(horBol)
				leido = ""
				
				mensaje_envio = str(idBol) + "," + str(idExp) + "," + fechaConc + "," + str(1)
				validacion = cliente.configSocket("autorizacion salida", mensaje_envio)
				print("VALIDACION: ",validacion)
				print(validacion,fechaConc)
				print(validacion,fechaConc)
				dh=self.restar_hora(horBol.split(':',2),fecBol.split('-'))
				
				try:
					
					dias=dh[0]
					horas=dh[1]
					minutos=dh[2]
					#horas=horas+(dias*24)
					#tiempoEstacionado=horas
					#print("DHDHDHDHDHDHDHDHDHD",dh)
					if(dias==0):
						if(minutos<tolerancia):
							
							validacion="finalizado"
							botones.abrir()
							print("abrido")
				except Exception as error:
					print("Errrr  Toleeee",error)
					pass
					
				



				
			#self.lboleto.setText(validacion)
			if validacion == "finalizado":
				self.f1 = self.f2 = self.f3 = True
				leyendaCandado = "VUELVA PRONTO"
			elif validacion == "salida candado":
				self.f1 = self.f2 = self.f3 = True
			elif validacion == "volver a pagar":
				self.lboleto.setText("---> 	Tiempo de salida excedido <---")
				#mixer.init()
				#mixer.music.load('/home/cajero/Documentos/eum/app/salida/sonidos/mensaje4.mp3')
				#mixer.music.play()
				self.f1 = False
				#self.stackedWidget.setCurrentIndex(4)
				validacion = ""
				pantalla_cont = 30
			elif validacion == "pago no realizado":
				self.lboleto.setText("---> Favor de pagar su boleto... <---")
				#mixer.init()
				#mixer.music.load('/home/cajero/Documentos/eum/app/salida/sonidos/mensaje2.mp3')
				#mixer.music.play()
				self.f1 = False
				validacion = ""
				pantalla_cont = 30
				#self.stackedWidget.setCurrentIndex(2)
			elif validacion == "error":
				"""
				este bloque representa las acciones frente a una desconexion
				"""
				self.f1 = self.f2 = self.f3 = True
				leyendaCandado = "VUELVA PRONTO s/c"
				#self.stackedWidget.setCurrentIndex(2)
				validacion = "finalizado"
			elif validacion == "boleto no encontrado":
				#mixer.init()
				self.lboleto.setText("(1)Un momento, ya lo atendemos")
				#mixer.music.load('/home/cajero/Documentos/eum/app/salida/sonidos/mensaje2.mp3')
				##mixer.music.load('/home/cajero/Documentos/eum/app/salida/sonidos/mensaje7.mp3')
				#mixer.music.play()
				self.f1 = False
				validacion = ""
				pantalla_cont = 1
			elif validacion == "boleto obsoleto":
				self.lboleto.setText("---> Boleto usado <---")
				#mixer.init()
				#mixer.music.load('/home/cajero/Documentos/eum/app/salida/sonidos/mensaje3.mp3')
				#mixer.music.play()
				self.f1 = False
				#self.stackedWidget.setCurrentIndex(3)
				validacion = ""
				pantalla_cont = 30
			elif validacion == "sin comunicacion servidor":
				#mixer.init()
				#mixer.music.load('/home/cajero/Documentos/eum/app/salida/sonidos/mensaje5.mp3')
				#mixer.music.play()
				self.f1 = False
				#self.stackedWidget.setCurrentIndex(5)
				validacion = ""
				pantalla_cont = 30
			elif validacion == "Candado Expirado":
				self.f1 = self.f2 = self.f3 = True
			
			
		
		if self.f1 == True and self.f2 == True:
			#self.stackedWidget.setCurrentIndex(6)
			pantalla_cont = 30
			if reproduccion == 0:
				if(validacion=="finalizado"):
					time.sleep(0.5)
					botones.abrir()
				elif(validacion=="salida candado"):
					time.sleep(0.5)
					botones.abrir()
				else:
					estado = 3
				self.lboleto.setText(leyendaCandado)
				
				reproduccion = 1
				
			#time.sleep(2)
			print("estado:",estado)
			#botones.leerBobina2Subida()
			if(estado == 1):
				
				if(botones.leerBobina2Subida()):
					print("Auto sobre segundo sensor")
					estado = 2
				else :
					print("Esperando regreso")
					estado = 1
					
			elif(estado == 2):
				if(botones.leerBobina2Subida() == False):
					print("Esperando que el auto abandone segundo sensor")
					estado = 3
				else :
					print("Auto sobre segundo sensor")
					estado = 2
					
			elif(estado == 3):
				print("Secuencia finalizada")
				self.f1 = self.f2 = self.f3 = self.f4 = self.f5 = self.f6 = self.f7 = False
				leido = ""
				estado = 1
				validacion = ""
				reproduccion = 0
					
			"""if self.f3 == True:
				if self.f7 == False:
					time.sleep(0.5)
					botones.abrir()
					self.f7 = True
				self.f4 = botones.leerBobina2Subida()
				if self.f4 == True:
					print("Auto sobre el sensor")
					self.f5 = botones.leerBobina2Subida()
					print("Auto sobre el sensor2, self5",self.f5)
					if self.f5 == False:		
						self.f4 = False
						self.f3 = False
						print("Reestablezco secuencia")
			if self.f3 == False and self.f4 == False and self.f5 == True and self.f6 == False:
				self.f6 = botones.CerrarBarrera()
				if self.f6 == True:
					self.f5 = False
			if self.f3 == False and self.f4 == False and self.f5 == False and self.f6 == True:
				print ("Ya cerre barrera restablesco fs")
				self.f1 = self.f2 = self.f3 = self.f4 = self.f5 = self.f6 = self.f7 = False
				reproduccion = 0
			"""
		QtCore.QTimer.singleShot(100, self.leerBotones)

	def fechaLabel(self):
		fecha = fechaUTC.fechaConFormato()
		self.ldate2.setText(fecha)
		
		hora = fechaUTC.tiempoConFormato()
		self.ltime2.setText(hora)

	def restar_hora(self,horab,fechab):
		global aux_dif
		"""formato = "%H:%M:%S"
		h1 = datetime.strptime(hora1, formato)
		h2 = datetime.strptime(hora2, formato)
		resultado = h1 - h2
		aux_dif=str(resultado)
		print("res:",h1,h2,resultado,type(str(resultado)))
		return str(resultado)"""
		fechaBoleto = datetime.strptime(str(fechab[0]) + str(fechab[1]) + str(fechab[2]), '%d%m%Y').date()
		horaBoleto = datetime.strptime(str(horab[0]) +':'+str(horab[1]) +':'+ str(horab[2]), '%H:%M:%S').time()
		fechaActual=datetime.now().date()
		horaActual=datetime.now().time()
		horayFechaBoleto = datetime.now().combine(fechaBoleto, horaBoleto)
		horayFechaActual = datetime.now().combine(fechaActual, horaActual)
		restaFechas = horayFechaActual - horayFechaBoleto
		aux_dif=str(restaFechas)
		dias = int(restaFechas.days)
		horas = int(restaFechas.seconds / 3600)
		minutos= int(restaFechas.seconds / 60)
		return dias,horas,minutos
		
		
		
	

	def cam(self):
		print("reiniciando...")
		thread1 = Thread(target = activarCamara, args=())
		try:
			a=thread1.start()
			print("hiulo1",a)
		except Exception:
			pass
		#os.system("sudo wmctrl -r 'zbar' -e 0,950,780,250,170")
		
		#os.system("sudo wmctrl -r 'Dialog' -e 0,0,-30,1900,1050")
		#os.system("sudo wmctrl -a 'zbar'")
		
		#os.system("sudo shutdown -P 0")

	def reiniciarRasp(self):
		os.system("sudo shutdown -r 0")
	def apagarRasp(self):
		os.system("sudo shutdown 0")

	def validarConf(self):
		if(os.path.exists("keyboard.conf")):
			f=open("keyboard.conf", "r")
			contents =f.read()
			if('1' in contents):
				configurado = "Ya esta configurado"
				return True
			else:				
				print("Configurando...")
				self.confMetodTeclado()
		else:				
			print("Configurando...")
			self.confMetodTeclado()

	def confMetodTeclado(self):		
		command = 'dpkg-reconfigure keyboard-configuration'
		p = os.system('sudo -S %s' % (command))
		print(1, file=open("keyboard.conf", "a"))
		command = 'reboot'
		p = os.system('sudo -S %s' % (command))
		return True

def obtenerPlazaYLocalidad():
	pass

def obtenerIdSal():
	global idSal
	try:
		connection = psycopg2.connect(user=usuario, password=contrasenia, database=bd, host='localhost')
		with connection.cursor() as cursor:
			cursor.execute(
				' SELECT num_salida FROM datos_salida WHERE id_salida = 1')
			row = cursor.fetchone()
			if row is not None:
				print("columns: {}".format(row[0]))
				idSal = int(row[0])
				connection.commit()
				connection.close()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)

def hilos():
	thread = Thread(target = activarFuncion, args=())
	thread1 = Thread(target = activarCamara, args=())
	thread2 = Thread(target = pollConexion, args=())

	try:
		thread.start()
		thread2.start()
		thread1.start()
	except Exception:
		pass
def buscaCamara():
	global camInicial
	while(1):
		lee2 = os.system("sudo find /dev -name 'video*' > cam.txt")
		a = open("cam.txt", "r")
		cam=(a.readline().rstrip("\n")).lstrip("\x00")
		a.close()
		a = open("cam.txt", "w")
		a.write('')
		time.sleep(1)
		print('Cammmmmmmmm',cam,camInicial)
		if(cam!=camInicial):
			print('Camara desconectadaaaaaaaaa')
			os.system("sudo pkill zbarcam")
			
def leerCodQR():
	global camInicial
	time.sleep(1)
	lee2 = os.system("sudo find /dev -name 'video*' > cam.txt")
	a = open("cam.txt", "r")
	cam=(a.readline().rstrip("\n")).lstrip("\x00")
	a.close()
	a = open("cam.txt", "w")
	a.write('')
	camInicial=cam
	print('CamInicial',camInicial)
	while(1):
		time.sleep(1)
		lee2 = os.system("sudo find /dev -name 'video*' > cam.txt")
		a = open("cam.txt", "r")
		cam=(a.readline().rstrip("\n")).lstrip("\x00")
		a.close()
		a = open("cam.txt", "w")
		a.write('')
		print('Cam',cam,camInicial)
		if(cam==camInicial):

			try:
				print('Camara Detectada')
				lee = os.system("sudo zbarcam --raw  --prescale=280x150  "+cam+"  >> datos.txt")
				#lee = os.system("zbarcam --raw  --prescale=10x10 /dev/video0 > /home/cajero/Documentos/eum/app/caseta/ticket.txt")
				#lee = os.system("/home/cajero/Documentos/eum/app/caseta/dsreader -l 27 -b 14 -r 30 -s 100 -u 50  > /home/cajero/Documentos/eum/app/caseta/ticket.txt")
				#lee = os.system("cd /home/pi/scanner/dsreader")
				#lee = os.system("./dsreader -l 27 -b 14 -r 30 -s 100 -u 50  > /home/cajero/Documentos/eum/app/caseta/ticket.txt")

			except e:
				mensajeTolerancia=1
				print("Error al crear el socket: ",e)
		else:
			
			if(cam!=''):
				camInicial=cam
			else:
				print('Camara desconectada')


def activarCamara():
	try:
		print('Camara Detectada')
		lee = os.system("sudo zbarcam --raw  --prescale=280x150 >> datos.txt")
		#lee = os.system("zbarcam --raw  --prescale=10x10 /dev/video0 > /home/cajero/Documentos/eum/app/caseta/ticket.txt")
		#lee = os.system("/home/cajero/Documentos/eum/app/caseta/dsreader -l 27 -b 14 -r 30 -s 100 -u 50  > /home/cajero/Documentos/eum/app/caseta/ticket.txt")
		#lee = os.system("cd /home/pi/scanner/dsreader")
		#lee = os.system("./dsreader -l 27 -b 14 -r 30 -s 100 -u 50  > /home/cajero/Documentos/eum/app/caseta/ticket.txt")

	except e:
		mensajeTolerancia=1
		print("Error al crear el socket: ",e)
	
def pollConexion():
	time.sleep(6)

	print("TAB TAB......")
	print("TAB TAB......")
	print("TAB TAB......")
	print("TAB TAB......")
	print("TAB TAB......")
	print("TAB TAB......")
	print("TAB TAB......")
	print("TAB TAB......")
	print("TAB TAB......")
	print("TAB TAB......")
	print("TAB TAB......")
	
	os.system("xdotool click 1")
	print("Click Undecorate")
	time.sleep(1)
	os.system("xdotool key Tab")
	os.system("xdotool key Tab")
	os.system("xdotool key Tab")
	while(1):
		pollearConexion()
		time.sleep(1)
	

def pollearConexion():
	global conexion_activa, leido, leyendaCandado, validacion
	conexion_activa = conexion.activo()
	print("conexion:",conexion_activa)
	if(1):
		#Validando candado
		if("CHT" in leido):
			try:
				print("leido endpoint:",leido)
				folio = leido.split(" ")
				folio = folio[0]
				print("leido endpoint2:",folio)
				folio  = folio[3:]
				print("Folio:",folio)
				endpoint="https://parkingtip.pythonanywhere.com/api/suscripciones/"+str(4)+"/?clave="+str(folio)
				r = requests.get(endpoint)
				print("STATUS_CODE: ",r.status_code,r)
				try:
					data = json.loads(r.text)[0]
					print("data: ",data)
					vigencia=data["activo"]
					nombre=data["nombre"]
					leyendaCandado = "Hasta pronto"+nombre
					print("vigencia:", endpoint, vigencia,nombre)
					if(vigencia):
						try:
							if(conexion_activa):
								validacion = cliente.configSocket("gerencia", folio)
								print("registro gerencia: ",validacion)
						except:
							print("error al insertar gerencia: ")
						
						validacion = "salida candado"
						print("Abriendo a locatario/pensionado",r.status_code)
					else:
						leyendaCandado = "Candado expirado"
						validacion = "Candado Expirado"
						print("Candado Expirado")
				except: 
					print("endpoint inalcanzable",r.status_code)
					leyendaCandado = "Endpoint inalcanzable: "+str(r.status_code)
					validacion = "Candado Expirado"
					print("Candado Expirado")
				leido = ""
			except:
				#leido = ""
				busy = mixer.get_busy()
				print("Busy:", busy)
				busy = mixer.get_busy()
				print("Busy:", busy)
				busy = mixer.get_busy()
				print("Busy:", busy)
				'''
				mixer.init()
				mixer.music.load('/home/cajero/Documentos/eum/app/salida/sonidos/mensaje4.mp3')
				busy = mixer.get_busy()
				print("Busy:", busy)
				mixer.music.play()'''
				leyendaCandado = "... S/C ..."
				print("Sin conexion al exterior")
				validacion = "salida candado"

	else:
		if(leido != ""):
			#botones.abrirBarrera()
			validacion = "finalizado"
			print("Sin conexion al servidor")
			leido = ""

	




def activarFuncion():
	import sys
	app = QApplication(sys.argv)
	ui = Ui_ventanaAcceso()
	ui.show()
	app.exec_()

if __name__ == "__main__":	
	hilos()
	obtenerIdSal()
	conexion = Conexiones()
	cola = Pila()
	time.sleep(3)
	os.system("xprop -f _MOTIF_WM_HINTS 32c -set _MOTIF_WM_HINTS '0x2, 0x0, 0x0, 0x0, 0x0'")

	
	
