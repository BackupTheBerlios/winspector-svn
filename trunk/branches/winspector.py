#!/usr/bin/env python
# -*- coding: iso-8859-1  -*-
############################################################################
# 
#  Del original Copyright (C) 2004-2005 Trolltech AS. All rights reserved. 
#  De las ampliaciones Copyright (C) 2010 Alberto Cardona
# 
#  
# 
#  This file may be used under the terms of the GNU General Public
#  License version 2.0 as published by the Free Software Foundation
#  and appearing in the file LICENSE.GPL included in the packaging of
#  this file.  Please review the following information to ensure GNU
#  General Public Licensing requirements will be met:
#  http://www.trolltech.com/products/qt/opensource.html
# 
#  
# 
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
# 
############################################################################

# ver python para todos.pdf pagina 113 para compartir informacion entre procesos
import sys
import pickle
import time
import string
import pyttsx
import logging



from commands import *
from forms.frmWinspector import Ui_frmWinspector
from PyQt4 import QtCore, QtGui, QtNetwork
from modulos.iwlibs import Wireless,  getWNICnames # funcion refrescar para saber que dispositivos tenemos
from modulos.generales import *

class MainWindow(QtGui.QMainWindow): 
    def __init__(self, parent=None):
        ''' Inicializa la clase ventana principal del programa
        '''
        logging.basicConfig(level= logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='./Winspector.log',
                    filemode='w')
        self.Debug= False  # poner a false como uso normal
        QtGui.QMainWindow.__init__(self, parent)
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Oxygen'))
        #Inicializar el formulario
        self.ui = Ui_frmWinspector()
        self.ui.setupUi(self)
        self.connect(self.ui.actionModo_Debug, QtCore.SIGNAL("triggered()"), self.activaDebug)
        self.MantenEscaneo= False
        self.TopeGrafica = 500
        self.AnchoBarra = 2
        self.Voz = False
        self.AltoLetrero = self.ui.Label1.geometry().y() 
        self.NombresComparativa=[]
        self.DispositivosWifi = [] # Lista de todos los dispositivos que van ha utilizarse para el escaneo, solo estan los seleccionados
        self.Parametros = {}  # guarda los parametros del programa para guardarlos y volverlos a cargar cada vez que arrancamos el programa
                    #                    Parametros['Senalindice'] = 0
                    #                    Parametros['Calidadindice'] = 0
                    ##                   Estos dos se utilizan para mantener un indice a las señales que estamos comparando, para que al pulsar uno de los cuatro botones la señal 
                    ##                   se desplace
                    #                    Parametros['Conectado'] = None
                    ##                    Cuando estamos conectados a un ap aqui se guarda la linea de la tabla
                    #                    Parametros['ModoCompara']= False
                    ##                    Cuando estamos comparando vale True si estamos en modo captura vale false
                    #                    Parametros['Bsside'] = None 
                    ##                    Contiene la mac del ap al que nos conectamos para la grafica y demas
                    #                    Parametros['Dispositivo'] = None
                    ##                    Es el dispositivo inalambrico usado para la conexion con el ap,
                    ##                    que junto con Bsside y Esside nos permiten saber la linea de la tabla que es
                    #                    Parametros['rutadescarga'] = self.ui.lineEdit.text()
                    ##                    Guarda la ruta completa al fichero para hacer las descargas de prueba
                    #                    Parametros['Vecesdescarga'] = self.ui.spinBoxv.value()
                    ##                    Cuantas veces tenemos que descargar el fichero 
                    #                    Parametros['intervalodescarga']= self.ui.spinBox.value()
                    ##                    Cuanto tiempo dejamos pasar entre dos descarga
                    #                    Parametros['CheckDescarga'] = self.ui.checkBox1.checkState()
                    ##                    Se ha seleccionado hacer la descarga en el checkbox
                    #                    Parametros['CheckPing']= self.ui.checkBox2.checkState()
                    ##                    Se ha seleccionado hacer los pings en el checkbox
                    #                    Parametros['CheckAuditoria'] = self.ui.checkBox3.checkState()
                    ##                    Se ha seleccionado hacer la auditoria en el checkbox
                    #                    Parametros['cuantosIps'] =  self.ui.spinBoxip.value()
                    ##                      Cuantos pings se lanzan cada vez 
                    #                    Parametros['DireccionIp']= self.ui.lineEditip.text()
                    ##                    Direccion Ip para hacer los pings
                    #                    Parametros['Tarjeta'] = self.ui.comboBoxDispo.currentText()
                    ##                    Contiene el dispositivo inalambrico que usabos para las capturas, cuando son varios se guardan en DispositivosWifi y aqui ponemos un signo ?
                    #                    Parametros['Quemuestro'] = self.ui.tristateBox.checkState()
                    ##                    Contiene el valor guardado del box triestate, para saber que se muestra en la captura de datos, la Señal, la Calidad o Ambos
                    #                    Parametros['ComparaSenal'] = self.ui.radioButton.isChecked()
                    ##                    Guarda por defecto  si queremos comparar la calidad o la señal de dos capturas
                    #                    Parametros['intervaloescaneo'] = self.ui.spinBoxescaneo.value()
                    ##                    Intervalo de tiempo entre dos escaneos
                    #                    Parametros['intervalopings'] =  self.ui.spinBoxip2.value()
                    ##                    Intervalo de tiempo entre dos lanzamientos de dos bloques de pings
                    #                    Parametros['AnchoBarra'] = self.ui.horizontalSlider.value()
                    ##                    Ancho de las barras de señal de la grafica en pixels
                    #                    Parametros['Esside'] = miItema36.text()
                    ##                    Nombre del ap seleccionado
                    
                    ##                     Si los tres sistemas de sonido son False no se usa ningun sistema de sonido
                    #                    Parametros['Festival']
                    ##                     si es True se usa el sistema de sonido festival 
                    #                    Parametros['Pyttsx']
                    ##                     si es True se usa el sistema de sonido pyttsx
                    #                    Parametros['Espeak']
                    ##                     si es True se usa el sistema de sonido Espeak
        self.Grafico=[] #señales capturadas de la ap actual que se muestran en la grafica, ejemplo [0, ' ', 0, 0], [99, '07:35:38', 11, 1], [99, '07:35:39', 11, 0]]
        self.LanLanSenal=[] # guarda las señales capturadas de cada ap capturada, ejemplo [[-88, -88, -87, -85, -84, -82, -86, -89], [-99]]
        self.LanLanCalidad=[] # guarda las calidades de señal de cada ap capturada  ejemplo [[25, 24, 22, 24, 25], [12, 10, 10]]
        self.LanLanTiempo=[] #guarda los tiempos en que se ha escaneado la señal
        self.CuandoInicioCaptura= None # Guarda el dia cuando se inicio la captura por si dura varios dias
        self.Lans={} # Guarda toda la informacion de todas las AP detectadas y que luego se muestra en la rejilla ejemplo
                             #{(' 00:16:38:CB:FD:C0', 'Max'): '-103', (' 00:16:38:CB:FD:C0', 'Mode'): 'Master', (' 00:16:38:CB:FD:C0', 'Min'): '-103', 
                             #(' 00:16:38:CB:FD:C0', 'Bssid'): ' 00:16:38:CB:FD:C0', (' 00:16:38:CB:FD:C0', 'Encri'): 'on', (' 00:16:38:CB:FD:C0', 'Senal'): '-103', 
                             #(' 00:16:38:CB:FD:C0', 'AGV'): '103.0',(' 00:16:38:CB:FD:C0', 'MDEV'): '206.0', (' 00:16:38:CB:FD:C0', 'Canal'): '3', 
                             #(' 00:16:38:CB:FD:C0', 'Essid'): 'WLAN_XX', (' 00:16:38:CB:FD:C0','Link'): '7'}
        self.LanLan = [] # Guarda una relacion de las AP detectadas, ejemplo [[' 00:16:38:CB:FD:C0', 'WLAN_XX', 0], [' 00:01:38:E2:F9:60', 'WLAN_XY', 1]]  
        self.CambiaTexto  = 5 # Cuando llega a cero cambiamos la etiqueta de la grafica    
        self.IndiceEtiqueta = 1 # etiqueta a mostrar 
        self.LanComparauno=[] # valores para comparar en el grafico
        self.LanComparaunoBis=[]
        self.LanComparados=[] # valores para comparar en el grafico
        self.LanComparadosBis=[]
        self.cargaConfiguracion()
        self.Parametros['Senalindice'] = 0
        self.Parametros['Calidadindice'] = 0
        self.Parametros['Conectado'] = None
        self.Parametros['ModoCompara']= False
        self.Parametros['Bsside'] = None 
        self.Parametros['Dispositivo'] = None
        self.Parametros['Esside'] = None
        self.cargainicial = True
        self.AltoGrafica = 180
        self.ProporcionAlto = 8.2
        self.sc = QtGui.QGraphicsScene()
        self.sc.setSceneRect(0, 0, self.TopeGrafica, self.AltoGrafica)
        self.sc.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        self.ui.Label1.setText('')
        self.ui.Label2.setText('')        
        self.ui.Label3.setText('')
        self.ui.Label4.setText('')               
        self.ui.Label5.setText('')
        self.ui.Label6.setText('')        
        self.ui.Label7.setText('')
        self.ui.Label8.setText('')                   
        self.ui.Label9.setText('')
        self.ui.Label10.setText('')        
        self.ui.Label11.setText('')
                 
        for ele in range(self.TopeGrafica // self.AnchoBarra):
            self.Grafico.append([0, ' ', 0, 0])
        # ancho columnas tabla    
        self.ui.view.setColumnWidth(0, 25)
        self.ui.view.setColumnWidth(1, 130) 
        self.ui.view.setColumnWidth(2, 120)
        self.ui.view.setColumnWidth(3, 25)    
        self.ui.view.setColumnWidth(4, 60)
        self.ui.view.setColumnWidth(5, 30)  
        self.ui.view.setColumnWidth(6, 35)
        self.ui.view.setColumnWidth(7, 30) 
        self.ui.view.setColumnWidth(8, 35)
        self.ui.view.setColumnWidth(9, 35)    
        self.ui.view.setColumnWidth(10, 60)
        self.ui.view.setColumnWidth(11, 60)
        self.ui.view.setColumnWidth(12, 65)
        self.ui.view.setColumnWidth(13, 40)
        self.valoresiniciales()
        self.refrescar()  
        self.iconre0 = QtGui.QIcon()
        self.iconre0.addPixmap(QtGui.QPixmap(":/Ruta/Info/nw0.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.iconre1 = QtGui.QIcon()
        self.iconre1.addPixmap(QtGui.QPixmap(":/Ruta/Info/nw1.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)   
        self.iconre2 = QtGui.QIcon()
        self.iconre2.addPixmap(QtGui.QPixmap(":/Ruta/Info/nw2.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.iconre3 = QtGui.QIcon()
        self.iconre3.addPixmap(QtGui.QPixmap(":/Ruta/Info/nw3.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)          
        self.iconre4 = QtGui.QIcon()
        self.iconre4.addPixmap(QtGui.QPixmap(":/Ruta/Info/nw4.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        if (self.Parametros['Festival'] == False) & (self.Parametros['Pyttsx'] == False) & (self.Parametros['Espeak'] == False):
            self.ui.toolButton_3.setVisible(False)
        self.statusBar().showMessage(self.tr("Listo"))
       
        
    def cargaConfiguracion(self):
        ''' Coje los parametros guardados en el disco para utilizarlos en el programa        '''
        with open('./Info/configura.pickle', 'rb') as f:    
             self.Parametros = pickle.load(f)  
        
    def grabar(self):
        return
        
    def imprimir(self): 
        return
    def cerrar(self): 
        return
    def about(self): 
        ''' Muestra el mensaje Acerca de'''
        QtGui.QMessageBox.about(self, self.tr("Acerca de Auditor scan"),
            self.tr("El <b>WInspector</b> permite analizar "
                    " dispositivos y antenas wireless"
                    " para poder comparar, cual da mas calidad"
                    " y mejora las conexiones."))
        return
        
    def comprobarIPintroducida(self): 
        ''' Comprueba la IP introducida para que este dentro de los rangos validos'''
        valor = compruebaIp(self.ui.lineEditip.text())
        self.ui.lineEditip.setText(valor[1])
        if valor[0] == 1:
            self.ui.lineEditip.setFocus()
        elif valor[0] == 2:
            self.actualizarparametros()
        else:
            QtGui.QMessageBox.about(self, self.tr("ERROR"), self.tr("Error en el programa en comprobacion de ip"))
        
    def actualizarparametros(self): 
        ''' Cuando actualizamos un parametro de la configuracion se guardan en el diccionario Parametros'''
        if self.cargainicial != True:
            self.Parametros['rutadescarga'] = self.ui.lineEdit.text()
            self.Parametros['Vecesdescarga'] = self.ui.spinBoxv.value()
            self.Parametros['intervalodescarga']= self.ui.spinBox.value()
            self.Parametros['CheckDescarga'] = self.ui.checkBox1.checkState()
            self.Parametros['CheckPing']= self.ui.checkBox2.checkState()
            self.Parametros['CheckAuditoria'] = self.ui.checkBox3.checkState()
            self.Parametros['cuantosIps'] =  self.ui.spinBoxip.value()    
            self.Parametros['DireccionIp']= self.ui.lineEditip.text()
            self.Parametros['Tarjeta'] = self.ui.comboBoxDispo.currentText()
            self.Parametros['Quemuestro'] = self.ui.tristateBox.checkState()
            self.Parametros['ComparaSenal'] = self.ui.radioButton.isChecked()
            self.Parametros['intervaloescaneo'] = self.ui.spinBoxescaneo.value()
            self.Parametros['intervalopings'] =  self.ui.spinBoxip2.value()
            self.Parametros['AnchoBarra'] = self.ui.horizontalSlider.value()
            self.Parametros['Festival'] = self.ui.festivalbox.isChecked() 
            self.Parametros['Pyttsx'] = self.ui.pyttsxbox.isChecked() 
            self.Parametros['Espeak'] = self.ui.espeakbox.isChecked() 
            self.statusBar().showMessage( QtGui.QApplication.translate("winspector", "Actualizado", None, QtGui.QApplication.UnicodeUTF8),   1000)
        if  self.ui.tristateBox.checkState() == QtCore.Qt.Checked:
            self.ui.tristateBox.setText(QtGui.QApplication.translate("frmWinspector", "&Ambos", None, QtGui.QApplication.UnicodeUTF8))
        elif self.ui.tristateBox.checkState() == QtCore.Qt.PartiallyChecked:
            self.ui.tristateBox.setText(QtGui.QApplication.translate("frmWinspector", "&Señal", None, QtGui.QApplication.UnicodeUTF8))
        elif self.ui.tristateBox.checkState() == QtCore.Qt.Unchecked:    
            self.ui.tristateBox.setText(QtGui.QApplication.translate("frmWinspector", "&Calidad", None, QtGui.QApplication.UnicodeUTF8))
        return
        
    def refrescar(self):                                              # Represca el combobox con los dispositivos disponibles
        ''' Ejecuta al pulsar el boton de refresco de dispositivos'''
        Actual = self.Parametros["Tarjeta"]
        self.ui.comboBoxDispo.clear()
        ## Los motivos para usar getWNICnames y no implementar aqui la funcion directamente es que si no encuentra en el fichero proc/net/wireless nada
        ## esa funcion del las python-wifi consulta al kernel

        for iface in getWNICnames():
            self.ui.comboBoxDispo.addItems([iface])
        self.ui.comboBoxDispo.addItems(['?'])    
        self.Parametros["Tarjeta"] = Actual    
        elemento = self.ui.comboBoxDispo.findText(self.Parametros['Tarjeta'])
        if elemento > 0 : 
            self.ui.comboBoxDispo.setCurrentIndex(elemento)
        else:
            self.ui.comboBoxDispo.setCurrentIndex(0)    
            self.Parametros['Tarjeta'] = self.ui.comboBoxDispo.currentText()   
        if self.MantenEscaneo == False:
            self.MantenEscaneo = True
        print self.DispositivosWifi
        return
        
    def VariosDispositivos(self, Cual):                      # selecciona varios dispositivos para hacer el escaneo
        '''Al pulsar sobre los dispositivos lo añade a la lista y les añade un icono, al volverlos a seleccionar los quita de la lista, 
        todos los que esten seleccionados son escaneados si el interrogante ? esta como dispositivo elegido
        Cual es el activado'''
        icon53 = QtGui.QIcon()   
        if self.ui.comboBoxDispo.itemText(Cual) == '?':
            self.DispositivosWifi =[]
            for dispo in range( self.ui.comboBoxDispo.count()):
                if dispo != Cual:
                    self.DispositivosWifi += [str(self.ui.comboBoxDispo.itemText(dispo))]

        if  self.ui.comboBoxDispo.itemText(Cual) in self.DispositivosWifi:
            self.ui.comboBoxDispo.setItemIcon(Cual, icon53 )
            Lista = self.DispositivosWifi
            self.DispositivosWifi = []
            for elemento in Lista:
                if (elemento != self.ui.comboBoxDispo.itemText(Cual)) & (elemento != '?'):
                    self.DispositivosWifi += [elemento]
        
        else:    
            icon53.addPixmap(QtGui.QPixmap(":/Ruta/Info/wifi.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            self.ui.comboBoxDispo.setItemIcon(Cual, icon53 )
            self.DispositivosWifi += [str(self.ui.comboBoxDispo.itemText(Cual))]



    def scanear(self): 
        ''' Ejecuta cuando pulsamos boton escaneo        '''
        if Escaneado.isRunning():
            self.MantenEscaneo = False
        else:
            self.MantenEscaneo = True    
        if self.MantenEscaneo:
            LogoAnima.start()
            Escaneado.start()
            self.CuandoInicioCaptura = time.strftime("%j %d %m %y", time.localtime())
       #     self.ui.frame_2.setVisible(True)
        else:
            self.ui.toolButtono.setIcon(self.iconre0)
            LogoAnima.terminate()
            Escaneado.terminate() 
          #  self.ui.frame_2.setVisible(False)
            if len(self.LanLanSenal) > 0:
                self.ui.ButtonGuarda.setVisible(True)   
        return

    def guardar(self): 
        ''' Guarda los Parametros a disco         '''
        self.actualizarparametros()
        with open('./Info/configura.pickle', 'wb') as f:    
            pickle.dump(self.Parametros, f) 
        return
        
    def activaDebug(self):    
        self.Debug = not self.Debug
        
        
        
    def altavoz(self):                                                   # al pulsar el boton de altavoz lo activa
        self.iconvoz = QtGui.QIcon()
        if self.Voz:
            self.Voz = False
            self.iconvoz.addPixmap(QtGui.QPixmap(":/Ruta/Info/irc-unvoice.png"), QtGui.QIcon.Normal, QtGui.QIcon.On) 
        else:
            self.Voz = True
            self.iconvoz.addPixmap(QtGui.QPixmap(":/Ruta/Info/irc-voice.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                #Se inicia el motor de voz
            if self.Parametros['Pyttsx']:
                self.engine = pyttsx.init()
                #Se selecciona el idioma a utilizar
                self.engine.setProperty('voice', "spanish-latin-american")
        self.ui.toolButton_3.setIcon(self.iconvoz)  
        return

    def Sinvoz(self):
        '''cuando pulsamos en el combo box que desactiva el sistema de sonido ejecutamos esta funcion'''
        self.actualizarparametros()    
        if (self.Parametros['Festival'] == False) & (self.Parametros['Pyttsx'] == False) & (self.Parametros['Espeak'] == False):
            self.ui.toolButton_3.setVisible(False)
        else:
            self.ui.toolButton_3.setVisible(True)

        

    def valoresiniciales(self):                                     # carga los valores iniciales guardados en parametros en los witgets
        '''Establece los witgets a los valores guardados por defecto'''
            # valores iniciales   
        self.ui.spinBoxv.setValue(self.Parametros["Vecesdescarga"])
        self.ui.spinBox.setValue(self.Parametros["intervalodescarga"])
        self.ui.lineEdit.setText( self.Parametros["rutadescarga"])
        self.ui.checkBox1.setChecked( self.Parametros['CheckDescarga'])
        self.ui.checkBox2.setChecked( self.Parametros['CheckPing'])    
        self.ui.checkBox3.setChecked( self.Parametros['CheckAuditoria'])   
        self.ui.lineEditip.setText( self.Parametros["DireccionIp"])
        self.ui.spinBoxip.setValue(self.Parametros["cuantosIps"])
        self.ui.tristateBox.setCheckState(  self.Parametros['Quemuestro'])
        self.ui.radioButton.setChecked( self.Parametros['ComparaSenal'] )
        self.ui.spinBoxescaneo.setValue(self.Parametros['intervaloescaneo'])
        self.ui.spinBoxip2.setValue(self.Parametros['intervalopings'])
        self.ui.festivalbox.setChecked(self.Parametros['Festival'])
        self.ui.pyttsxbox.setChecked( self.Parametros['Pyttsx'])
        self.ui.espeakbox.setChecked( self.Parametros['Espeak'] )

        
        self.ui.botondere2.setEnabled(False)  
        self.ui.botondere1.setEnabled(False)  
        self.ui.botonizqui1.setEnabled(False)  
        self.ui.botonizqui2.setEnabled(False)  
        if not self.ui.radioButton.isChecked():
            self.ui.radioButton_2.setChecked(True)
        self.ui.frame.setVisible(False)
        self.ui.frame_2.setVisible(True)
        self.ui.verticalSlider.setProperty("value", 0)
        self.ui.verticalSlider_2.setProperty("value", 0)        
        self.ui.horizontalSlider.setProperty("value", self.Parametros['AnchoBarra']) 
        self.ui.horizontalSlider_2.setProperty("value", self.Parametros['AnchoBarra'])   
        self.crearmarcas()
        self.ui.graphicsView.setScene(self.sc)
        self.cargainicial = False
        
    def crearmarcas(self):
        ''' Crea las marcas con los niveles de señal en la grafica'''
        zoOm = self.ui.verticalSlider.value()
        if self.Parametros['ModoCompara']:
            zoOm = self.ui.verticalSlider_2.value()        
       #]# if self.Debug:
            #]# #]# logging.debug('>>>>>>ENTRO FUNCION CREAMARCAS')
            #]# logging.debug(zoOm)
        if zoOm == 0:
            for altomarca in range(10, 110, 10):
                self.creaMarca(altomarca, altomarca)
        elif zoOm == 1:
                self.creaMarca( 10, 80)
                self.creaMarca( 55, 90)
                self.creaMarca( 100, 100)
        elif zoOm == 2:
                self.creaMarca( 10, 60)
                self.creaMarca( 55, 70)
                self.creaMarca( 100, 80)        
        elif zoOm == 3:
                self.creaMarca( 10, 40)
                self.creaMarca( 55, 50)
                self.creaMarca( 100, 60)               
        elif zoOm == 4:
                self.creaMarca( 10, 20)
                self.creaMarca( 55, 30)
                self.creaMarca( 100, 40)               
        elif zoOm == 5:
                self.creaMarca( 10, 10)
                self.creaMarca( 55, 20)
                self.creaMarca( 100, 30)                   
                
    def creaMarca(self, altomarCa, altoDibu):        
        ''' Crea cada una de las marcas
            Parametros :
                Altomarca la altura donde se pondra la marca
                Altodibu nombre que recibe el dibujo para pintarlo
        '''
        pen2 = QtGui.QPen(QtGui.QColor(240, 240, 0), 0,  QtCore.Qt.DotLine, QtCore.Qt.RoundCap)    
        lineal1 = int ( altomarCa * (self.sc.sceneRect().height()/100)) 
       #]# if self.Debug:
            #]# logging.debug('FUNCION CREAMARCA')
            #]# logging.debug(lineal1)
            #]# logging.debug(altomarCa)
            #]# logging.debug(self.sc.sceneRect().height())
            #]# logging.debug('........................')
        self.sc.Linea = QtGui.QGraphicsLineItem(10, lineal1 , self.sc.sceneRect().width() + 5,  lineal1)
        self.sc.Linea.setPen(pen2)
        self.sc.addItem(self.sc.Linea)
        imagen = QtGui.QPixmap( ':/Ruta/Info/' + str(altoDibu) + '.png')
        cifra = QtGui.QGraphicsPixmapItem(imagen)
        cifra.setOffset(-10, lineal1-3)
        self.sc.addItem(cifra)
   
  
    def modotrabajo(self):                                          # cambia entre captura y comparacion
        '''Al pulsar el boton que cambia entre modo compara y modo captura'''
        icon33 = QtGui.QIcon()    
        if self.ui.frame.isVisible():
            self.ui.horizontalSlider_2.setProperty("value", self.AnchoBarra) 
            icon33.addPixmap(QtGui.QPixmap(":/Ruta/Info/nw4.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            self.ui.btmodo.setText("Modo Captura")
            self.ui.frame.setVisible(False)
            self.ui.frame_2.setVisible(True)  
            self.ui.botondere2.setEnabled(False)  
            self.ui.botondere1.setEnabled(False)  
            self.ui.botonizqui1.setEnabled(False)  
            self.ui.botonizqui2.setEnabled(False)
            self.Parametros['ModoCompara'] = False
            if self.Parametros['Conectado'] !=None:
                GraficaAnima.start()
                LogoAnima.start()
                Escaneado.start()
        
        else:               
            self.ui.horizontalSlider.setProperty("value", self.AnchoBarra) 
            if self.Grafico[-1][0] != 0:
                boton = QtGui.QMessageBox.question(None,
                    self.trUtf8("Borro las señales del grafico"),
                    self.trUtf8("""Si quiere comparar

    (Si) Comparar dos señales guardadas
    (No) Comparar la actual con otra guardada"""),
                    QtGui.QMessageBox.StandardButtons(\
                        QtGui.QMessageBox.No | \
                        QtGui.QMessageBox.Yes ),
                    QtGui.QMessageBox.No)
                if boton == QtGui.QMessageBox.Yes: 
                    for ele in range(self.TopeGrafica // self.AnchoBarra):
                        self.Grafico.pop(0)
                        self.Grafico.append([0, ' ', 0, 0])         
                    self.CambiaTexto  = 5 # Cuando llega a cero cambiamos la etiqueta de la grafica    
                    self.IndiceEtiqueta = 1   
            icon33.addPixmap(QtGui.QPixmap(":/Ruta/Info/comparar.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            self.ui.btmodo.setText("Modo Compara")
            self.ui.frame.setVisible(True)
            self.ui.frame_2.setVisible(False)
            self.Parametros['ModoCompara'] = True
            LogoAnima.terminate()
            Escaneado.terminate() 
        self.ui.btmodo.setIcon(icon33)    
        
        

        
    def CambiaNombreDispositivo(self):                  # pendiente
        print 'cambiar nombre dispositivos'
        

  
    def cambiadispositivo(self, Dispositivo):              # al cambiar el dispositivo en el combobox se ejecuta esta funcion
        ''' Al cambiar el dispositivo inalambrico se ejecuta esta funcion'''
        if (len(self.DispositivosWifi)== 0) & (self.Parametros['Tarjeta'] == '?'):
            self.ui.comboBoxDispo.setCurrentIndex(-1)
        else:    
            self.Parametros['Tarjeta'] = Dispositivo
        
    def desplaza1(self):
        self.recargagrafico(2, -1)

    def desplaza2(self):
        self.recargagrafico(2, 1) 

    def desplaza3(self):
        self.recargagrafico(1, -1) 
 
    def desplaza4(self):
        self.recargagrafico(1, 1) 

    def cambialineas(self):                                         # punto de entrada para generar el grafico
        ''' Repinta el grafico es llamada desde el Thread cada cierto tiempo'''
        iniciO1 = self.sc.sceneRect().height()
        self.crealineas(iniciO1 / 100)

 
    def zoom(self, Pos):
        ''' Cuando cambia el zoom ejecuta esta rutina'''       
        self.cambialineas()
        
    def AmpliarGrafica(self):    
        pass
        
    def GuardarUno(self):
        self.GuardaCapturas(False)

    def GuardarTodos(self):
        self.GuardaCapturas(True)

    def GuardaCapturas(self, Todos):
        '''Guarda las señales capturadas a disco
        Parametro todos vale true o false'''
    #    print self.Grafico
        swPregunta = True
        if Todos:
            for ele in self.LanLan:
                if swPregunta:
                    boton = QtGui.QMessageBox.question(None,
                    self.trUtf8("Guardo las señales de este AP"),
                    self.trUtf8("""Guardo las señales de este AP

    (Si) para guardar este AP
    (No) para no guardar este AP
    (Si a todo) para Guardar todos sin preguntar"""),
                    QtGui.QMessageBox.StandardButtons(\
                        QtGui.QMessageBox.No | \
                        QtGui.QMessageBox.Yes | \
                        QtGui.QMessageBox.YesToAll),
                    QtGui.QMessageBox.YesToAll)
                if boton == QtGui.QMessageBox.YesToAll:
                    swPregunta = False
                    swBoton=True
                if boton == QtGui.QMessageBox.Yes:
                    swBoton= True   
                if swBoton: 
                    GuardaLecturas(self.LanLanSenal[ele[2]], self.LanLanCalidad[ele[2]],  ele[1],  self.LanLanTiempo[ele[2]],  self.CuandoInicioCaptura,  ele[3])    
        else:              
            for ele in self.LanLan:
                if   (self.Parametros['Bsside'] in ele)  &  (self.Parametros['Dispositivo'] in ele):
                    GuardaLecturas(self.LanLanSenal[ele[2]], self.LanLanCalidad[ele[2]],  ele[1],  self.LanLanTiempo[ele[2]],  self.CuandoInicioCaptura,  ele[3] )
        
    def onClickTable(self,  miIema):
        ''' Cuando pulsamos sobre un AP de la lista ejecutamos estas ordenes'''
        LiNea = miIema.row()
        if self.Parametros['Conectado'] == LiNea:
             GraficaAnima.terminate()
             
        if self.Parametros['Conectado'] != None:   # Si es la primera vez que pulsamos sobre un AP pero ya habiamos elegido otro antes
            miItema34 = QtGui.QTableWidgetItem()                   
            miItema34.setText( ' ' )
            self.iconcon = QtGui.QIcon()
            miItema34.setIcon(self.iconcon)
            self.ui.view.setItem(self.Parametros['Conectado'],0,miItema34)
                         
                
        if self.Parametros['Conectado'] !=LiNea: # Si hemos pulsado sobre un AP distinto del que ya habiamos pulsado o es la primera vez
            GraficaAnima.start()
            self.Parametros['Conectado'] = LiNea
            miItema33 = QtGui.QTableWidgetItem()   
            self.iconcon = QtGui.QIcon()
            self.iconcon.addPixmap(QtGui.QPixmap(":/Ruta/Info/user-online.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            miItema33.setIcon(self.iconcon)
            self.ui.view.setItem(LiNea ,0,miItema33)
            miItema35 = QtGui.QTableWidgetItem()
            miItema35= self.ui.view.item(LiNea, 2)
            miItema36 = QtGui.QTableWidgetItem()
            miItema36= self.ui.view.item(LiNea, 1)
            miItema38 = QtGui.QTableWidgetItem()
            miItema38= self.ui.view.item(LiNea, 12)
            self.Parametros['Bsside'] = miItema35.text()
            self.Parametros['Esside'] = miItema36.text()
            Tarjetaa =str(miItema38.text())
            self.Parametros['Dispositivo'] = string.strip(Tarjetaa)
            self.RenuevaelGrafico()
        
    def RenuevaelGrafico(self):                             # Al cambiar de Ap o al cambiar el ancho de barra, recarga el grafico
        self.Grafico = []
        for ele in range(self.TopeGrafica // self.AnchoBarra):
            self.Grafico.append([0, ' ', 0, 0]) 
        self.CambiaTexto  = 5 # Cuando llega a cero cambiamos la etiqueta de la grafica    
        self.IndiceEtiqueta = 1
        for ele in self.LanLan:
            if  (self.Parametros['Bsside'] in ele) & (self.Parametros['Dispositivo'] in ele):
                Tope = len(self.LanLanSenal[ele[2]])
                if Tope > (self.TopeGrafica // self.AnchoBarra):
                    Tope =  len(self.LanLanSenal[ele[2]]) - (self.TopeGrafica // self.AnchoBarra)
                    Topede = range( Tope ,  (self.TopeGrafica // self.AnchoBarra))
                else:
                    Topede = range(Tope)
                for cual in Topede:
                    self.CambiaTexto -=1
                    if self.CambiaTexto == 0:
                        etiqueta = self.IndiceEtiqueta
                     #   self.CambiaTexto = 30
                        Cuantos =len(self.DispositivosWifi)
                        if Cuantos == 0 :
                            Cuantos=1
#                        if self.AnchoBarra == 1:
#                            self.CambiaTexto = 100 * Cuantos
#                        else:
                        self.CambiaTexto = (50 * self.AnchoBarra) * Cuantos
                    else:
                        etiqueta = 0
                    self.IndiceEtiqueta += 1
                    if self.IndiceEtiqueta == 12:
                        self.IndiceEtiqueta = 1     
                        
                    self.Grafico.pop(0)    
                    self.Grafico.append([abs( int( self.LanLanSenal[ele[2]][cual])), self.LanLanTiempo[ele[2]][cual] , abs( int(  self.LanLanCalidad[ele[2]][cual])), etiqueta ]) 
       # self.Controletiqueta()   
          
    
    def crealineas(self, Multiplicador):   
        ''' Crea todo el self.Grafico pasandole como valor la altura del self.Grafico dividida por 100'''
        Fina = int(self.sc.sceneRect().height())
      #  Ancho = self.sc.sceneRect().width() 
        Zoom = self.ui.verticalSlider.value()
        if self.Parametros['ModoCompara']:
            Zoom = self.ui.verticalSlider_2.value()
            estadoBox = QtCore.Qt.Checked
        else:
            estadoBox = self.ui.tristateBox.checkState()
    #    Ancho = Ancho // (self.TopeGrafica // self.AnchoBarra)    
      #  Saltar = int(Ancho) 
        Saltar = self.AnchoBarra
        self.sc.clear()
        self.crearmarcas()
        penVerde = QtGui.QPen(QtGui.QColor(0, 255, 0), Saltar, QtCore.Qt.SolidLine, QtCore.Qt.SquareCap)    # lineas de la señal
        penAma = QtGui.QPen(QtGui.QColor(253,253, 0 ), Saltar, QtCore.Qt.SolidLine, QtCore.Qt.SquareCap)    # lineas de la calidad
        penRojo = QtGui.QPen(QtGui.QColor(164, 33, 33), Saltar, QtCore.Qt.SolidLine, QtCore.Qt.SquareCap)   
        penNegro =QtGui.QPen(QtGui.QColor(0, 0, 0), Saltar, QtCore.Qt.SolidLine, QtCore.Qt.SquareCap)   
        x=12
        #self.Controletiqueta()                 
        for indice in range((self.TopeGrafica // self.AnchoBarra)-1):
            
            if self.Debug:
                 logging.debug('CREALINEAS CALCULO ALTURA PARAMETROS ENVIADOS A LA FUNCION CALCULO ALTURA')
                 logging.debug([Zoom, self.Grafico[indice][0], self.Grafico[indice][2], Multiplicador, Fina, estadoBox])
            if   (self.Grafico[indice][0] == 0) & (self.Grafico[indice][2] == 0):   
                Resultado=[Fina, Fina, Fina,  Fina]
            else:    
                Resultado = calculoaltura(Zoom, self.Grafico[indice][0], self.Grafico[indice][2], Multiplicador, Fina, estadoBox ,  self.ProporcionAlto)
            if self.Debug:
                 logging.debug('CREALINEAS CALCULO ALTURA VALORES RETORNADOS')
                 logging.debug(Resultado)            
                 logging.debug('SI SON IGUALES LA SEÑAL Y LA CALIDAD CAMBIA EL COLOR A ROJO')
                 logging.debug(str(self.Grafico[indice][0]) + '  ' + str(self.Grafico[indice][2]))
            if (self.Grafico[indice][0] == self.Grafico[indice][2]) & (self.Parametros['ModoCompara']):
                if self.Debug:
                     logging.debug('CREALINEAS  SI SON IGUALES LA SEÑAL Y LA CALIDAD')
                penUno = penRojo
                penDos = penRojo
            else:
                if self.Debug:
                     logging.debug('CREALINEAS NO SON IGUALES LA SEÑAL Y LA CALIDAD')                
                penUno = penAma
                penDos = penVerde
            if   Resultado[0]  == 0:
                penUno = penNegro
            if   Resultado[2]  == 0:
                penDos = penNegro                
            print ' s ' + str(self.Grafico[indice][0])    
            if  (self.ui.tristateBox.checkState() == QtCore.Qt.Checked) | (self.ui.tristateBox.checkState() == QtCore.Qt.Unchecked) | (self.Parametros['ModoCompara']):
                if (Resultado[2] !=0)  & (self.Grafico[indice][2] !=0) :               
                    self.crealinea(self.Grafico[indice], x,  Resultado[1],  Resultado[3],  penUno, 0)                
            if  (self.ui.tristateBox.checkState() == QtCore.Qt.Checked) | (self.ui.tristateBox.checkState() == QtCore.Qt.PartiallyChecked) | (self.Parametros['ModoCompara']):
                if (Resultado[0] !=0)  & (self.Grafico[indice][0] !=0):
                    self.crealinea(self.Grafico[indice], x,  Resultado[0],  Resultado[2],  penDos, 1)
            x += Saltar     
    
    def Controletiqueta(self):
        '''Cada 70 recorridos marca el grafico para realizar la marca de texto '''
        if self.Parametros['Conectado'] != None:
            self.CambiaTexto -= 1
        if self.CambiaTexto == 0:
            self.Grafico[(self.TopeGrafica // self.AnchoBarra)-1][3]  = self.IndiceEtiqueta
            Cuantos =len(self.DispositivosWifi)
            if Cuantos == 0 :
                Cuantos=1
#            if self.AnchoBarra == 1:
#                self.CambiaTexto = 100 * Cuantos
#            else:
            self.CambiaTexto = (50 * self.AnchoBarra) * Cuantos
            self.IndiceEtiqueta += 1
            if self.IndiceEtiqueta == 12:
                self.IndiceEtiqueta = 1

        
    def ControletiquetaCorre(self,  Donde,  Quien,  Texto):
        '''Cuando hay que imprimir una etiqueta esta funcion identifica cual es y la mueve'''
        Donde = Donde + 50
        if Donde < 63:
            Texto = ''
        if Quien == 1:
            self.ui.Label1.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15))  
            self.ui.Label1.setText(Texto)
        if Quien == 2:
            self.ui.Label2.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15))  
            self.ui.Label2.setText(Texto)      
        if Quien == 3:
            self.ui.Label3.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15))  
            self.ui.Label3.setText(Texto)   
        if Quien == 4:
            self.ui.Label4.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15)) 
            self.ui.Label4.setText(Texto)   
        if Quien == 5:
            self.ui.Label5.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15))  
            self.ui.Label5.setText(Texto)   
        if Quien == 6:
            self.ui.Label6.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15))  
            self.ui.Label6.setText(Texto)   
        if Quien == 7:
            self.ui.Label7.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15))  
            self.ui.Label7.setText(Texto)   
        if Quien == 8:
            self.ui.Label8.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15)) 
            self.ui.Label8.setText(Texto)   
        if Quien == 9:
            self.ui.Label9.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15))  
            self.ui.Label9.setText(Texto)   
        if Quien == 10:
            self.ui.Label10.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15))  
            self.ui.Label10.setText(Texto)  
        if Quien == 11:
            self.ui.Label11.setGeometry(QtCore.QRect(Donde, self.AltoLetrero, 37, 15))  
            self.ui.Label11.setText(Texto)  


    def crealinea(self, Valor,  x, Altollega,  Fina,  pen,  delimitador):
        ''' Dibuja cada una de las lineas
            Parametros 
                Valor una lista con los valores [Señal, Hora escaneo, Calidad señal, Crear Marca]
                x Coordenada de desplazamiento lateral
                Altollega altura a la que llega la barra en el grafico
                Fina Altura real del grafico
                Pen  objeto pen para el dibujo de las lineas
                delimitador si vale uno dibuja la linea para el texto de abajo
        '''

        if  (Valor[3] != 0) & (delimitador == 1):
            #]# if self.Debug:
                #]# logging.debug('>>>>>>>>>>>>>>>>>>>>>>>>>>ENTRO FUNCION CREALINEA')
                #]# logging.debug([Valor,  x, Altollega,  Fina, pen.color().value(),  delimitador])
            penLinea = QtGui.QPen(QtGui.QColor(164, 33, 33), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)         
            self.sc.Linea = QtGui.QGraphicsLineItem(x, Fina +2 ,  x,  Fina + 20)
            self.sc.Linea.setPen(penLinea)
            self.sc.addItem(self.sc.Linea)
            self.ControletiquetaCorre(x, Valor[3], str(Valor[1]))
        self.sc.Linea0 = QtGui.QGraphicsLineItem(x, Altollega ,  x,  Fina)
        self.sc.Linea0.setPen(pen)
        if self.Parametros['ModoCompara']:
            self.sc.Linea0.setToolTip('Primera : ' + str(Valor[0]) + '\nSegunda ' + str(Valor[2])  + '\n\nMomento escaneo :' + str(Valor[1]) )  
        else:
            self.sc.Linea0.setToolTip('Señal : -' + str(Valor[0]) + '\nCalidad ' + str(Valor[2]) + '/70' + '\n\nMomento escaneo :' + str(Valor[1]) + '\nDispositivo :' + self.Parametros['Dispositivo'])            
        self.sc.addItem(self.sc.Linea0)

    
    def recargagrafico(self, cuaL,  Hacia):
        ''' Los valores son
            cuaL vale 1 o 2 dependiendo de si es señal o calidad de señal
            Hacia vale 0, 1 y -1 para 0 reinicia parametros , 1 o -1 mueve la señal hacia un lado u otro'''

        if len(self.NombresComparativa) == 2:    
            PrimeraLanComparada = 'WLan : ' + self.NombresComparativa[0][0] + '  Con :' + self.NombresComparativa[0][1] + ' -> ' + self.NombresComparativa[0][2] 
        else:
            PrimeraLanComparada = ''
        if len(self.NombresComparativa) == 2:
            SegundaLanComparada ='WLan : ' + self.NombresComparativa[1][0] + '  Con :' + self.NombresComparativa[1][1] + ' -> ' + self.NombresComparativa[1][2] 
        else:
            SegundaLanComparada =''

        self.ui.botondere2.setEnabled(True)  
        self.ui.botondere1.setEnabled(True)  
        self.ui.botonizqui1.setEnabled(True)  
        self.ui.botonizqui2.setEnabled(True)  
        ActualGrafica = self.TopeGrafica // self.AnchoBarra
        if (cuaL == 1) & (Hacia == 0):
            self.Parametros['Senalindice'] = 0
        elif (cuaL == 2) &  (Hacia == 0):
            self.Parametros['Calidadindice'] = 0
            
        if cuaL == 1:
            self.Parametros['Senalindice'] += Hacia
            if self.Parametros['Senalindice'] > len(self.LanComparauno) - ActualGrafica:
                self.Parametros['Senalindice'] = len(self.LanComparauno) - ActualGrafica
                self.ui.botondere2.setEnabled(False)   
            if self.Parametros['Senalindice'] < 0:
                self.Parametros['Senalindice'] = 0
                self.ui.botonizqui2.setEnabled(False)  
              

        elif cuaL == 2:
            self.Parametros['Calidadindice'] += Hacia  
            if self.Parametros['Calidadindice'] > len(self.LanComparauno) - ActualGrafica:
                self.Parametros['Calidadindice'] = len(self.LanComparauno) - ActualGrafica
                self.ui.botondere1.setEnabled(False)  
            if self.Parametros['Calidadindice'] < 0:
                self.Parametros['Calidadindice'] = 0
                self.ui.botonizqui1.setEnabled(False) 
        iniTio = self.Parametros['Senalindice'] 
        iniTio2 = self.Parametros['Calidadindice']

        for ele in range( iniTio,  iniTio + ActualGrafica ):
                if self.Parametros['Senalindice'] + ele > len(self.LanComparauno)-1:
                    break 
                self.Grafico[ele - self.Parametros['Senalindice']][0]=  self.LanComparauno[self.Parametros['Senalindice'] + ele ]
                if self.Parametros['Senalindice'] + ele > len(self.LanLanTiempo)-1:
                    break 
                self.Grafico[ele - self.Parametros['Senalindice']][1]=  '\n   Primera señal a las ' +  self.LanLanTiempo[self.Parametros['Senalindice'] + ele ] + '\n' + PrimeraLanComparada 
        for ele in range( iniTio2,  iniTio2 + ActualGrafica ): 
                if self.Parametros['Calidadindice'] + ele > len(self.LanComparados)-1:
                    break
                self.Grafico[ele  - self.Parametros['Calidadindice']][2]=   self.LanComparados[self.Parametros['Calidadindice'] + ele]   
                if self.Parametros['Calidadindice'] + ele > len(self.LanLanTiempo)-1:
                    break
                self.Grafico[ele  - self.Parametros['Calidadindice']][1] += '\n   Segunda señal a las ' + self.LanLanTiempo[self.Parametros['Calidadindice'] + ele ] + '\n' + SegundaLanComparada  #+ '/nComparando : ' + self.NombresComparativa[0] + '/nCon/n' +self.NombresComparativa[1] 
        self.cambialineas()
 
                
    def compara(self):                                              # Ejecuta la comparacion, pidiendo las señales a comparar
        '''Al pulsar en comparar se ejecuta esta funcion'''
       # aqui carga desde fichero el grafico bis 

        if self.Grafico[(self.TopeGrafica // self.AnchoBarra)-1][0] != 0 :
            Val = LeeLecturas(1)
            if Val[0]:    
                for ele in self.LanLan:
                    if  (self.Parametros['Bsside'] in ele)  & (self.Parametros['Dispositivo'] in ele): 
                        self.NombresComparativa= Val[5]
                        self.LanComparauno = self.LanLanSenal[ele[2]]
                        self.LanComparaunoBis = self.LanLanCalidad[ele[2]] #calidad 1
                self.LanComparados = DevuelveAlista(Val[1])
                self.LanComparadosBis = DevuelveAlista(Val[2] ) # calidad 2
                self.LanLanTiempo= DevuelveAlista(Val[3], 2)
                self.CuandoInicioCaptura = Val[4]
        else:
            Val = LeeLecturas(2)
            if Val[0]:    
                self.NombresComparativa= Val[5]
                self.LanComparauno = DevuelveAlista(Val[1]) #señal 1
                self.LanComparados = DevuelveAlista(Val[6] ) # Señal 2      
                self.LanComparaunoBis =DevuelveAlista( Val[2]) # Calidad 1
                self.LanComparadosBis = DevuelveAlista(Val[7] )   # Calidad 2  
                self.LanLanTiempo= DevuelveAlista(Val[3], 2)
                self.CuandoInicioCaptura = Val[4]
               #]# if self.Debug:
                    #]# logging.debug('COMPARA leo dos señales')
                    #]# logging.debug(self.LanComparauno)
                    #]# logging.debug(self.LanComparados)       
                    #]# logging.debug(self.LanComparaunoBis)
                    #]# logging.debug(self.LanComparadosBis)
       # print self.NombresComparativa
        if self.ui.radioButton_2.isChecked():    
                self.comparacambiacalidad()      
        if self.ui.radioButton.isChecked():
            self.recargagrafico(1, 0)
        elif self.ui.radioButton_2.isChecked():
            self.recargagrafico(2, 0)
      #  GraficaAnima.start()    
        self.cambialineas()
        self.Controletiqueta()
        


    def comparacambiasenal(self):
       #]# if self.Debug:
            #]# logging.debug('COMPARACAMBIASEÑAL ENTRO')
            #]# logging.debug(self.LanComparauno)
            #]# logging.debug(self.LanComparados)
            #]# logging.debug(self.LanComparaunoBis)
            #]# logging.debug(self.LanComparadosBis)            
        Temporal= self.LanComparaunoBis 
        self.LanComparaunoBis = self.LanComparauno
        self.LanComparauno = Temporal
    
        Temporal= self.LanComparadosBis 
        self.LanComparadosBis = self.LanComparados
        self.LanComparados = Temporal     
        self.recargagrafico(1, 0)
       #]# if self.Debug:
            #]# logging.debug('COMPARACAMBIASEÑAL SALGO')
            #]# logging.debug(self.LanComparauno)
            #]# logging.debug(self.LanComparados)  
            #]# logging.debug(self.LanComparaunoBis)
            #]# logging.debug(self.LanComparadosBis)   
        self.cambialineas()
            
    def comparacambiacalidad(self):
       #]# if self.Debug:
            #]# logging.debug('COMPARACAMBIACALIDAD ENTRO')   
            #]# logging.debug(self.LanComparauno)
            #]# logging.debug(self.LanComparados)  
            #]# logging.debug(self.LanComparaunoBis)
            #]# logging.debug(self.LanComparadosBis)  
            
        Temporal= self.LanComparauno 
        self.LanComparauno = self.LanComparaunoBis
        self.LanComparaunoBis = Temporal 
    
        Temporal= self.LanComparados 
        self.LanComparados = self.LanComparadosBis
        self.LanComparadosBis = Temporal     
        self.recargagrafico(2, 0)
       #]# if self.Debug:
            #]# logging.debug('COMPARACAMBIACALIDAD SALGO')
            #]# logging.debug(self.LanComparauno)
            #]# logging.debug(self.LanComparados)  
            #]# logging.debug(self.LanComparaunoBis)
            #]# logging.debug(self.LanComparadosBis)    
        self.cambialineas()
  

    def iniciar(self):
        ''' Se ejecuta cuando pulsamos el boton de iniciar auditoria
        '''
        self.ui.commandLinkButton.hide()
        self.Parametros["intervalodescarga"] = self.ui.spinBox.value()
        ProximaDescarga = time.time()
        ProximoPing = time.time()
        Mantenerauditoria = True
        DetenerauditoriaDescarga = False
        while Mantenerauditoria:
         #   self.statusBar().showMessage( str(time.time() - ProximaDescarga ), 5000)     habria que poner tambien proximoping y proximo escaneo
            if  self.ui.checkBox1.checkState() == QtCore.Qt.Checked:
                    # descarga
                DetenerauditoriaDescarga = self.IniciarDescarga(ProximaDescarga)
            else:
                DetenerauditoriaDescarga = True
            if  self.ui.checkBox2.checkState() == QtCore.Qt.Checked:
                        # ping  
                DetenerauditoriaPing = self.IniciarPings(ProximoPing)    
            else:
                DetenerauditoriaPing = True
            if self.ui.checkBox3.checkState() == QtCore.Qt.Checked:
                    # auditoria
                    print 'auditor'
            else:
                DetenerauditoriaComparar = True
            if (DetenerauditoriaComparar) & (DetenerauditoriaPing)  & (DetenerauditoriaDescarga):
                Mantenerauditoria = False
        self.ui.commandLinkButton.show()   
        return

    def IniciarPings(self,  ProximoPing):
        if ProximoPing < time.time(): 
            print 'ping'
            ProximoPing = ProximoPing + self.Parametros['intervalopings']
        return True

    def IniciarDescarga(self,  ProximaDescarga):   
        Vecesdescargar = self.Parametros['Vecesdescarga'] 
        if Vecesdescargar > 0 :
            if ProximaDescarga < time.time(): 
                Http =  HttpWindow()
                Http.exec_()
                miItema = QtGui.QTableWidgetItem()  
                miItema.setText( string.rjust(str(round( RespuestaAuditoria['DescargaVelocidad'], 2)) + ' KB/s', 8) )
                self.ui.tableWidget.insertRow(self.ui.tableWidget.rowCount() )
                self.ui.tableWidget.setItem(self.ui.tableWidget.rowCount() -1 ,0,miItema)
                self.ui.tableWidget.setRowHeight(self.ui.tableWidget.rowCount() -1, 15)
                ProximaDescarga = ProximaDescarga + self.Parametros["intervalodescarga"]
                Vecesdescargar -=1
                self.Parametros['Vecesdescarga'] = Vecesdescargar
                if Vecesdescargar == 0:
                    return False # Detenerauditoria se para
        return True

    def cambiaLogo(self,  icono):
        '''Cambia el icono del boton'''
        if not self.MantenEscaneo :
            icono = self.iconre0
        self.ui.toolButtono.setIcon(icono)

    def AnchoBarra(self, pos): 
        self.AnchoBarra = pos
        if  self.Parametros['ModoCompara']:
            if len(self.Grafico) < (self.TopeGrafica // self.AnchoBarra):
                for ele in range(len(self.Grafico),(self.TopeGrafica // self.AnchoBarra) ):
                    self.Grafico.append([0, ' ', 0, 0])             
            if self.ui.radioButton.isChecked():
                self.recargagrafico(1, 0)
            elif self.ui.radioButton_2.isChecked():
                self.recargagrafico(2, 0)
        else: 
            self.ui.Label1.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))  
            self.ui.Label2.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))   
            self.ui.Label3.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))  
            self.ui.Label4.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))               
            self.ui.Label5.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))  
            self.ui.Label6.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))   
            self.ui.Label7.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))  
            self.ui.Label8.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))                  
            self.ui.Label9.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))  
            self.ui.Label10.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))   
            self.ui.Label11.setGeometry(QtCore.QRect(self.TopeGrafica + 50, self.AltoLetrero, 37, 15))  
                
            self.RenuevaelGrafico()
        self.cambialineas()
       
    def RedibujoAp(self, Tarjeta ,  Bssid, Alta, linea):
        ''' Dibuja las la tabla de AP encontrada
          Bssid numero de Bssid del ap detectado
          Alta boolean true para alta de linea
          linea numerico si es modificar nos dice que linea tiene que modificar
        '''
        Tarjetaa = str(Tarjeta)
        Bssidd = str(Bssid)
        if Alta:
            self.ui.view.insertRow(self.ui.view.rowCount() )   
            self.ui.view.setItem(self.ui.view.rowCount() -1 ,0,QtGui.QTableWidgetItem(' ') )              
            self.ui.view.setItem(self.ui.view.rowCount() -1 ,1,QtGui.QTableWidgetItem(string.rjust(self.Lans[Tarjetaa, Bssidd, 'Essid'], 8))  )
            self.ui.view.setItem(self.ui.view.rowCount() -1 ,2,QtGui.QTableWidgetItem(string.rjust(self.Lans[Tarjetaa, Bssidd, 'Bssid'], 8) )  )    
            self.ui.view.setItem(self.ui.view.rowCount() -1 ,3,QtGui.QTableWidgetItem(string.rjust(self.Lans[Tarjetaa, Bssidd, 'Canal'], 2) )  )
            self.ui.view.setItem(self.ui.view.rowCount() -1 ,4, QtGui.QTableWidgetItem(string.rjust(self.Lans[Tarjetaa, Bssidd, 'Mode'], 8) )  )
            self.ui.view.setItem(self.ui.view.rowCount() -1 ,5,QtGui.QTableWidgetItem(str.strip(self.Lans[Tarjetaa, Bssidd, 'Encri']) )  )   
            linea= self.ui.view.rowCount() -1
        self.ui.view.setItem(self.ui.view.rowCount() -1 ,5,QtGui.QTableWidgetItem(str.strip(self.Lans[Tarjetaa, Bssidd, 'Encri']) )  )     
        self.ui.view.setItem(linea ,6,QtGui.QTableWidgetItem(string.rjust(self.Lans[Tarjetaa, Bssidd, 'Senal'], 3) )  )
        self.ui.view.setItem(linea ,7,QtGui.QTableWidgetItem(string.rjust(self.Lans[Tarjetaa, Bssidd, 'Link'], 3)) )                
        self.ui.view.setItem(linea ,8,QtGui.QTableWidgetItem( string.rjust(self.Lans[Tarjetaa, Bssidd, 'Min'], 3)) )
        self.ui.view.setItem(linea ,9,QtGui.QTableWidgetItem(string.rjust(self.Lans[Tarjetaa, Bssidd, 'Max'], 3))  )          
        self.ui.view.setItem(linea ,10,QtGui.QTableWidgetItem(string.rjust(self.Lans[Tarjetaa, Bssidd, 'AGV'], 8))  )
        self.ui.view.setItem(linea ,11,QtGui.QTableWidgetItem(string.rjust(self.Lans[Tarjetaa, Bssidd, 'MDEV'], 8))  )
        self.ui.view.setItem(linea ,12,QtGui.QTableWidgetItem(string.rjust(Tarjetaa, 8))  )        
        miItema37 = QtGui.QTableWidgetItem()
        miItema37= self.ui.view.item(linea, 13)
        if Alta:
            Valorde = 0
        else:    
            Valorde = int(miItema37.text())
        Valorde += 1
        self.ui.view.setItem(linea ,13,QtGui.QTableWidgetItem( str(Valorde ))  )          
      #  self.ui.view.setRowHeight(self.ui.view.rowCount() -1, 15)   

    def ApLeida(self, ApInfo):
       #]# if self.Debug:
            #]# logging.debug('>>>>>>>>>>>>>>>>>>>>>>>>>>ENTRO FUNCION APLEIDA')
            #]# logging.debug(ApInfo)
        if  (self.Parametros['Conectado'] != None) & (self.Parametros['Bsside'] == ApInfo['LanBssid']) & (self.Parametros['Dispositivo'] == ApInfo['Dispositivo']):
            ## pone la etiqueta
            self.CambiaTexto -=1
            if self.CambiaTexto == 0:
                etiqueta = self.IndiceEtiqueta
                self.CambiaTexto = 30
            else:
                etiqueta = 0
            self.IndiceEtiqueta += 1
            if self.IndiceEtiqueta == 12:
                self.IndiceEtiqueta = 1  
                
            self.Grafico.pop(0) 
            self.Grafico.append([abs( int(ApInfo['LanSenal'] )), ApInfo['Tiempo'] , abs( int(ApInfo['LanLink'] )), etiqueta ])  #time.strftime("%H:%M:%S", time.localtime())
            if (self.Voz) & (self.Parametros['ModoCompara'] == False):
 
            #Se genera la voz a partir de un texto
                if  (self.ui.tristateBox.checkState() == QtCore.Qt.Checked) | (self.ui.tristateBox.checkState() == QtCore.Qt.Unchecked):

                    if self.Parametros['Festival']:
                        status,  text= getstatusoutput('echo ' + ApInfo['LanLink']  + ' | festival --tts')

                    if self.Parametros['Espeak']:
                        Valors = str( ApInfo['LanLink'] )
                        if  int(ApInfo['LanLink'])  < 0:
                            Valors = 'menos ' + str(abs(int(Valors)))         
                        status,  text= getstatusoutput('espeak -ves "' + Valors + '"' )

                    if self.Parametros['Pyttsx']:
                        self.engine.say(ApInfo['LanLink'])
                        self.engine.runAndWait()                        
                if (self.ui.tristateBox.checkState() == QtCore.Qt.Checked) | (self.ui.tristateBox.checkState() == QtCore.Qt.PartiallyChecked):

                    if self.Parametros['Festival']:
                        status,  text= getstatusoutput('echo menos ' + ApInfo['LanSenal']  + ' | festival --tts')
                    if self.Parametros['Espeak']:
                        Valors = str( ApInfo['LanSenal'] )
                        if  int(ApInfo['LanSenal'])  < 0:
                            Valors = 'menos ' + str(abs(int(Valors)))         
                        status,  text= getstatusoutput('espeak -ves "' + Valors + '"' )

                    if self.Parametros['Pyttsx']:
                        self.engine.say(ApInfo['LanSenal'])
                        self.engine.runAndWait()
                #Se reproduce la voz

              
        swinserta = True
        Posicion = 0
        Posicion1 = 0
        Posicion2 = 0
        # comprueba que LanLan no tenga una bssid con ese numero
        # si lo tiene entonces swinserta pasa a false para no insertar otra
        for ele in self.LanLan:
            if  (ApInfo['LanBssid'] in ele) & (ApInfo['Dispositivo'] in ele):
                swinserta = False
                Posicion = ele[2]
                Posicion1 = ele[2]
                Posicion2 = ele[2]
   
        if swinserta:
            self.LanLanSenal.append([])
            Posicion = len(self.LanLanSenal)-1 
            self.LanLanCalidad.append([])
            Posicion1 = len(self.LanLanCalidad)-1 
            self.LanLanTiempo.append([])
            Posicion2 = len(self.LanLanTiempo)-1
            
       # Añande la senal medida a la lista de señales del ap
        Valores = self.LanLanSenal[Posicion]
        Valores.append(int(ApInfo['LanSenal'] ) ) 
        self.LanLanSenal[Posicion] = Valores
    # anade la calidad de señal a la lista de calidades de señal del ap
        Valores1 = self.LanLanCalidad[Posicion1]
        Valores1.append(int(ApInfo['LanLink']) ) 
        self.LanLanCalidad[Posicion1] = Valores1
        
    # anade el tiempo a la lista de tiempos del ap
        Valores2 = self.LanLanTiempo[Posicion2]
        Valores2.append(ApInfo['Tiempo'] ) 
        self.LanLanTiempo[Posicion2] = Valores2
        
        Cuantos = len(self.LanLanSenal[Posicion])
        Senales = self.LanLanSenal[Posicion]
 
        self.Lans[ApInfo['Dispositivo'],  ApInfo['LanBssid'], 'AGV'] = str( round(media(Cuantos, Senales), 2))
        self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'], 'MDEV'] =str( round( desviacionCuadratica(Cuantos,  Senales), 2 ))
        if swinserta:
            self.LanLan.append([ ApInfo['LanBssid'], ApInfo['LanEssid']  , len(self.LanLan),  ApInfo['Dispositivo']])                         
            self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'],  'Essid' ] =  ApInfo['LanEssid'] 
            self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'],  'Bssid' ] =  ApInfo['LanBssid']
            self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'],  'Canal' ] = ApInfo['LanCanal']
            self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'],  'Link' ] = ApInfo['LanLink']
            self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'],  'Senal' ] = ApInfo['LanSenal']     
            self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'],  'Encri' ] = ApInfo['LanEncri']         
            self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'],  'Mode' ] = ApInfo['LanMode']
            self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'], 'Min'] =ApInfo['LanSenal']
            self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'], 'Max'] =ApInfo['LanSenal']
            self.RedibujoAp(ApInfo['Dispositivo'], ApInfo['LanBssid'], True, 0)
        else:
            if  self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'], 'Min']  < ApInfo['LanSenal'] :
                self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'], 'Min'] = ApInfo['LanSenal'] 
                
            if  self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'], 'Max']  > ApInfo['LanSenal'] :
                self.Lans[ApInfo['Dispositivo'], ApInfo['LanBssid'], 'Max'] = ApInfo['LanSenal'] 

            for linea in range(self.ui.view.rowCount()):  
                mitema = self.ui.view.item(linea, 2)
                mitema2 =self.ui.view.item(linea, 12)
                QueTarjeta =string.strip(str(mitema2.text()))
                if (mitema.text() == ApInfo['LanBssid']) & ( QueTarjeta== ApInfo['Dispositivo']):
                    self.RedibujoAp(ApInfo['Dispositivo'], ApInfo['LanBssid'], False, linea)

    def dockCambia(self):
        print 'cambia dock'


class Escanear(QtCore.QThread):
    def run(self):
        ''' Ejecuta el escaneo de APs'''
        while mainwindow.MantenEscaneo:
            self.EscaneoAPCual()
            if mainwindow.ui.spinBoxescaneo.value() > 0:    
                time.sleep(mainwindow.ui.spinBoxescaneo.value())
                
    def EscaneoAPCual(self):            
        if  mainwindow.Parametros['Tarjeta'] != '?':
            self.EscaneoAP( mainwindow.Parametros['Tarjeta'] )
        else:
            for Tarjeta in mainwindow.DispositivosWifi:
                self.EscaneoAP(Tarjeta)

    def EscaneoAP(self,  Tarjeta): 
        """ Lee los AP cercanos ejecuta un iwlist Escaneando la wifi """  
        Cadena ='iwlist '  + str(Tarjeta)  +  ' scan'
        status,  text= getstatusoutput(Cadena )
        fichero = string.split(text, 'Cell' )
        self.LeeScan(fichero[1:], Tarjeta)
       
    def LeeScan(self,  fichero,  Tarjeta):
        '''  El resultado del escaneado es leido haciendo bloques por cell '''
        for celula in fichero:
            self.ApInfo={'LanBssid':'',  'LanLink':'', 'LanSenal':'', 'LanCanal':'', 'LanEssid':'', 'LanEncri':'', 'LanMode': '',  'Tiempo': '', 'Dispositivo': ''}
            self.ApInfo['Dispositivo']=  str(Tarjeta)
            linea =  string.split(celula, '\n')
            self.LeeCell(linea)   
            self.emit(QtCore.SIGNAL("ApLeida(PyQt_PyObject)"),self.ApInfo)    
            
    def LeeCell(self, celula): 
        for linea in celula:
            self.LeeCellLinea(linea)
           
            
    def LeeCellLinea(self, linea):
    
        ''' De cada Ap escaneado recoge la informacion 
        Si en el futuro cambia el formato de iwlist aqui es donde hay que corregirlo
        OJO si el escaneo retorna esto                     Quality:70/100  Signal level:-62 dBm  Noise level:-97 dBm
            entonces se recorre el elif ==4 pero si el valor recogido es                     Quality=25/70  Signal level=-85 dBm
            entonces se recorre el elif == 1
            esto depende de la tarjeta lo que devuelva
        '''
        info =  string.split(linea, ':')
        if len(info) == 7: # la bssid es de 7 campos [' 02 - Address', ' 02', '22', 'B0', '9B', 'EE', '40'] 
            self.ApInfo['LanBssid'] = string.strip(string.join( info[1:], ':'))  
        elif len(info) == 1: # de este valor son ['                    Quality=15/70  Signal level=-95 dBm  '] 
            texto = string.split(info[0], '=')  #['                    Quality'] 
            valor = string.strip(texto[0]) #[Quality] 
            if valor == 'Quality':
                textocalidad=string.split(texto[1], '/') #['15','70  Signal level'] 
 ##               textocalidad2= string.split(textocalidad[1], ' ')  #['70','Signal level'] 
                self.ApInfo['LanLink']  = textocalidad[0] #['15'] 
                textosenal= string.split(texto[2], ' ')  #['-95','dBm'] 

                self.ApInfo['LanSenal']  = textosenal[0] #['-95']
        elif  len(info) == 4:    # Quality:76/100  Signal level:-60 dBm  Noise level:-97 dBm    
            texto = string.split(info[0]) 
            valor = string.strip(texto[0]) #[Quality]     
            if valor == 'Quality':
                textocalidad=string.split(info[1], '/') #['15','70  Signal level'] 
                self.ApInfo['LanLink']  = textocalidad[0] #['15'] 
                textosenal= string.split(info[2], ' ')  #['-95','dBm'] 

                self.ApInfo['LanSenal']  = textosenal[0] #['-95']              
        else:
            Cual = string.split(linea, ':')
            if  string.strip(Cual[0]) == 'Channel':
                self.ApInfo['LanCanal']     = Cual[1]
            elif  string.strip(Cual[0]) == 'ESSID':
                essid = string.split(Cual[1], '"')
                self.ApInfo['LanEssid']    = essid[1]
            elif  string.strip(Cual[0]) == 'Encryption key':
                self.ApInfo['LanEncri']     = Cual[1]
            elif  string.strip(Cual[0]) == 'Mode':    
                self.ApInfo['LanMode']     = Cual[1]
        
        self.ApInfo['Tiempo'] =time.strftime("%H:%M:%S", time.localtime())
        return
        



 
class GraficaAnimada(QtCore.QThread):
    def run(self):
        ''' cada cierto tiempo llama al refresco de la grafica
        '''
        while True:
            self.emit(QtCore.SIGNAL("animagrafico"))    
            time.sleep(0.5)    

        
class LogoAnimado(QtCore.QThread):
    def run(self):
        ''' Cambia el logo del boton cada segundo
        '''
        icono = mainwindow.iconre0
        while mainwindow.MantenEscaneo: 
            if icono == mainwindow.iconre0:
                    icono = mainwindow.iconre1  
            elif icono == mainwindow.iconre1:
                    icono = mainwindow.iconre2         
            elif icono == mainwindow.iconre2:
                    icono = mainwindow.iconre3  
            elif icono == mainwindow.iconre3:
                    icono = mainwindow.iconre4
            elif icono == mainwindow.iconre4:
                    icono = mainwindow.iconre0        

            self.emit(QtCore.SIGNAL("animaLogo(QIcon*)"), icono) 
            time.sleep(1)
            



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mainwindow = MainWindow()
    LogoAnima = LogoAnimado()
    GraficaAnima = GraficaAnimada()
    Escaneado = Escanear()    
    QtCore.QObject.connect(GraficaAnima, QtCore.SIGNAL("animagrafico"), mainwindow.cambialineas, QtCore.Qt.QueuedConnection)
    QtCore.QObject.connect(LogoAnima, QtCore.SIGNAL("animaLogo(QIcon*)"), mainwindow.cambiaLogo, QtCore.Qt.QueuedConnection)      
    QtCore.QObject.connect(Escaneado, QtCore.SIGNAL("ApLeida(PyQt_PyObject)"), mainwindow.ApLeida, QtCore.Qt.QueuedConnection)      
    mainwindow.show()
    sys.exit(app.exec_())
