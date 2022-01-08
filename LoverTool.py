import os
import sys
import calendar
from datetime import date

from PyQt5 import uic
from PyQt5.QtCore import QDir, QDate, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDialog, QFileDialog, QListWidget, QDateEdit
from dateutil.relativedelta import relativedelta
import pickle

from servicio_chequear_fecha import Comprobar


def diferencia(inicio, actual=date.today()):
    dif = relativedelta(actual, inicio)
    semanas = dif.weeks
    dias = dif.days - (semanas*7)
    meses = dif.months
    annios = dif.years
    return ((actual - inicio).days, dias, semanas, meses, annios)

def cargar_datos_importantes():
    if os.path.isfile("config.data"):
        with open("config.data", "rb") as  f:
            config = pickle.load(f)
            return config

class LoversTool(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi("main.ui", self)
        self.servicio_alerta:Comprobar
        # ------------------------ #
        self.dia_especial = date.today()
        self.imagen = "img/heart.png"
        # ------------------------ #
        self.cargar_config()
        # ------------------------ #
        # evnto que ocurren con el cambio
        self.formato.currentIndexChanged.connect(self.init)
        self.aniv.dateChanged.connect(self.actualizar_fecha)
        self.nom1_edit.textChanged.connect(self.actualizar_nombre1)
        self.nom2_edit.textChanged.connect(self.actualizar_nombre2)
        # salvar config
        self.save.clicked.connect(self.guardar_config)
        # cargar imagen
        self.cambiar_img_btn.clicked.connect(self.cambiar_imagen)
        # ventana Datos importantes
        self.datos_window = DatosImportantes(self)
        self.datos_importantes.triggered.connect(self.datos_importantes_window)
        # acerca de
        self.acerca_de.triggered.connect(self.acerca_de_window)


    # COMBO BOX DE FORMATO
    @property
    def formato_tiempo_transcurrido(self):
        return self.formato.currentIndex()

    @formato_tiempo_transcurrido.setter
    def formato_tiempo_transcurrido(self, value):
        self.formato.setCurrentIndex(value)

    # LABELS DE NOMBRES
    @property
    def persona1(self):
        return self.nom1_edit.text().strip()

    @persona1.setter
    def persona1(self, value):
        self.nom1_edit.setText(value)

    @property
    def persona2(self):
        return self.nom2_edit.text().strip()

    @persona2.setter
    def persona2(self, value):
        self.nom2_edit.setText(value)

    @property
    def nombre1_value(self):
        return self.nombre1.text()

    @nombre1_value.setter
    def nombre1_value(self, value):
        self.nombre1.setText(value)

    @property
    def nombre2_value(self):
        return self.nombre2.text()

    @nombre2_value.setter
    def nombre2_value(self, value):
        self.nombre2.setText(value)

    # LABELS DE TIEMPO
    @property
    def tiempo_transcurrido(self):
        return self.tiempo.text()

    @tiempo_transcurrido.setter
    def tiempo_transcurrido(self, value):
        self.tiempo.setText(value)
        
    @property
    def tiempo_restante(self):
        return self.falta.format()
    
    @tiempo_restante.setter
    def tiempo_restante(self, value):
        self.falta.setFormat(value)

    @property
    def imagen_value(self):
        return self.imagen_lbl.pixmap()

    @imagen_value.setter
    def imagen_value(self, value):
        self.imagen_lbl.setPixmap(value)

    def init(self):
        try:
            # servicio para alertar fecha importante
            datos = cargar_datos_importantes()
            self.servicio_alerta = Comprobar({"aniversario":self.dia_especial, "cumple":datos["cumple"]}, self)
            # Actualizar el QDateEdit con la fecha especial
            self.aniv.setDate(self.dia_especial)
            # proximo aniversario
            prox = date(self.dia_especial.year + 1, self.dia_especial.month, self.dia_especial.day)
            # saco la diferencia
            dif = diferencia(self.dia_especial)
            annios = dif[4]
            meses = dif[3]
            semanas = dif[2]
            dias = dif[1]
            total_dias = dif[0]
            # cambiar los datos del No del Aniversario
            self.no_aniv.setText(f"{annios}º Aniversario" if annios else "Sin aniversario")
            # cambiar los datos del Tiempo de relacion
            tipo_f = self.formato_tiempo_transcurrido
            # cambiar los datos del Tiempo que falta para el proxim aniversarsio
            faltan = diferencia(date.today(), prox)
            faltan_meses = faltan[3]
            faltan_semanas = faltan[2]
            faltan_dias = faltan[1]
            faltan_total_dias = faltan[0]
            if not tipo_f:
                # TIEMPO TRANSCURRIDO
                self.tiempo_transcurrido = ""
                self.tiempo_transcurrido += f"{meses} meses " if meses else ""
                self.tiempo_transcurrido += f"{semanas} semanas " if semanas else ""
                self.tiempo_transcurrido += f"{dias} días " if dias else ""
                # TIEMPO RESTANTE
                self.tiempo_restante = "Faltan "
                self.tiempo_restante += f"{faltan_meses} meses " if faltan_meses else ""
                self.tiempo_restante += f"{faltan_semanas} semanas " if faltan_semanas else ""
                self.tiempo_restante += f"{faltan_dias} días" if faltan_dias else ""
                self.tiempo_restante += ", para el próximo aniversario"
            elif tipo_f == 1:
                self.tiempo_transcurrido = f"{total_dias} días"
                self.tiempo_restante = f"Faltan {faltan_total_dias} días, para el próximo aniversario"
            elif tipo_f == 2:
                self.tiempo_transcurrido = f"{meses} meses"
                self.tiempo_restante = f"Faltan {faltan_meses} meses, para el próximo aniversario"
            # BARRA DE PROGRESO
            porciento = total_dias * 100 / 366 if calendar.isleap(date.today().year) else 365
            self.falta.setValue(porciento)
        except Exception as e:
            self.error("Mostrando datos: " + e.args[0])

    def actualizar_fecha(self):
        qdate = self.aniv.date()
        self.dia_especial = date(qdate.year(), qdate.month(), qdate.day())
        self.init()

    def actualizar_nombre1(self):
        if not len(self.persona1):
            self.nombre1.setText("Sin nombre")
        else:
            self.nombre1.setText(self.persona1)

    def actualizar_nombre2(self):
        if not len(self.persona2):
            self.nombre2.setText("Sin nombre")
        else:
            self.nombre2.setText(self.persona2)

    # MOSTRAR VENTANA DATOS IMPORTANTES
    def datos_importantes_window(self):
        self.datos_window.show()

    def acerca_de_window(self):
        self.acerca_de = AcercaDe()

    # CAMBIAR LA IMAGEN
    def cambiar_imagen(self):
        nombreImagen, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen",
                                                      QDir.currentPath(),
                                                      "Archivos de imagen (*.jpg *.png *.bmp)")
        if nombreImagen:
            self.imagen = nombreImagen
            self.cargar_imagen()

    # PERSISTENCIA DE DATOS
    def validar(self):
        datos = {"Nombre 1":self.persona1, "Nombre 2":self.persona2}
        for i in datos:
            if not len(datos[i]):
                raise Exception(f"El campo {i} no puede estar vacío")

    def guardar_config(self):
        #try:
        self.validar()
        with open("config.setup", "wb") as  f:
            config = {"fecha":self.dia_especial, "formato":self.formato_tiempo_transcurrido, "nombres":[self.persona1, self.persona2], "imagen":self.imagen}
            pickle.dump(config, f)
        #except Exception as e:
            #self.error("Guardando datos: " + e.args[0])

    def cargar_config(self):
        #try:
        if os.path.isfile("config.setup"):
            with open("config.setup", "rb") as  f:
                config = pickle.load(f)
                self.dia_especial = config["fecha"]
                self.formato_tiempo_transcurrido = config["formato"]
                self.persona1 = config["nombres"][0]
                self.persona2 = config["nombres"][1]
                self.nombre1_value = config["nombres"][0]
                self.nombre2_value = config["nombres"][1]
                self.imagen = config["imagen"]
                self.cargar_imagen()
        self.init()
        #except Exception as e:
            #self.error("Cargando datos: " + str(e.args[0]))

    def cargar_imagen(self):
        if os.path.isfile(self.imagen):
            self.imagen_value = QPixmap(self.imagen)
        else:
            self.imagen_value = QPixmap("img/heart.png")

    def error(self, msg):
        QMessageBox.critical(self, "ERROR", msg)

#VENTANA DATOS IMPORTANTES
class DatosImportantes(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self)
        uic.loadUi("more.ui", self)
        self.parent = parent
        # --------------------------------
        # DECLARACIONES
        self.eventos:QListWidget
        # LLENAR
        self.eventos_importantes_lista = []
        self.canciones_dedicadas = []
        # --------------------------------
        self.predeterminado()
        self.cargar_config()
        # --------------------------------
        self.birthday.dateChanged.connect(self.birthday_data)
        self.add_evento.clicked.connect(self.anadir_evento)
        self.del_evento.clicked.connect(self.borrar_evento)
        self.eventos.itemClicked.connect(self.mostrar_info_evento)
        self.guardar.clicked.connect(self.guardar_config)

    @property
    def cruce_intereses_value(self):
        qdate = self.cruce_intereses.date()
        return date(qdate.year(), qdate.month(), qdate.day())

    @cruce_intereses_value.setter
    def cruce_intereses_value(self, value):
        self.cruce_intereses.setDate(value)

    @property
    def primera_cita_value(self):
        qdate = self.primera_cita.date()
        return date(qdate.year(), qdate.month(), qdate.day())

    @primera_cita_value.setter
    def primera_cita_value(self, value):
        self.primera_cita.setDate(value)

    @property
    def primer_beso_value(self):
        qdate = self.primer_beso.date()
        return date(qdate.year(), qdate.month(), qdate.day())

    @primer_beso_value.setter
    def primer_beso_value(self, value):
        self.primer_beso.setDate(value)

    @property
    def primera_vez_value(self):
        qdate = self.primera_vez.date()
        return date(qdate.year(), qdate.month(), qdate.day())

    @primera_vez_value.setter
    def primera_vez_value(self, value):
        self.primera_vez.setDate(value)
        
    @property
    def birthday_value(self):
        qdate = self.birthday.date()
        return date(qdate.year(), qdate.month(), qdate.day())

    @birthday_value.setter
    def birthday_value(self, value):
        self.birthday.setDate(value)
        
    @property
    def persona_cb_value(self):
        return self.persona_cb.currentText()
    
    @persona_cb_value.setter
    def persona_cb_value(self, value):
        self.persona_cb.setCurrentText(value)

    @property
    def edad_value(self):
        return
    
    @edad_value.setter
    def edad_value(self, value):
        self.edad.setValue(value)
        
    @property
    def edad_proxim_value(self):
        return
    
    @edad_proxim_value.setter
    def edad_proxim_value(self, value):
        self.edad_prox.setValue(value)
        
    @property
    def fecha_evento_value(self):
        qdate = self.fecha_evento.date()
        return date(qdate.year(), qdate.month(), qdate.day())
    
    @fecha_evento_value.setter
    def fecha_evento_value(self, value):
        self.fecha_evento.setDate(value)


    @property
    def descrip_evento_value(self):
        return self.descrip_evento.toPlainText().strip()

    @descrip_evento_value.setter
    def descrip_evento_value(self, value):
        self.descrip_evento.setText(value)

    def init(self):
        self.fecha_evento_value = date.today()
        # ----------------------
        self.birthday_data()
        # ---------------------- #
        self.actualizar_eventos()

    def predeterminado(self):
        fechas = (self.cruce_intereses, self.primera_cita, self.primer_beso, self.primera_vez, self.birthday)
        for i in fechas:
            i.setDate(date.today())

    def birthday_data(self):
        fecha = self.birthday_value
        dif = diferencia(fecha)
        edad = dif[4]
        dif_today = diferencia(date.today(), date(date.today().year+1, self.birthday_value.month, self.birthday_value.day))
        semanas = dif_today[2]
        dias = dif_today[1]
        meses = dif_today[3]
        # ---------------------------------------------------------------------------- #
        self.edad_value = edad
        self.edad_proxim_value = edad + 1
        # ------------------------------------ #
        progreso = dif_today[0] * 100 / 366 if calendar.isleap(date.today().year) else 365
        self.falta_birthday.setValue(progreso)
        txt = f"{meses} meses " if meses else ""
        txt += f"{semanas} semanas " if semanas else ""
        txt += f"{dias} días" if dias else ""
        self.falta_birthday.setFormat(txt)

    # EVENTOS
    def actualizar_eventos(self):
        self.eventos.clear()
        self.ordenar_eventos()
        for evento in self.eventos_importantes_lista:
            txt = f"{evento[0]} {evento[1]}"
            self.eventos.addItem(txt)

    def anadir_evento(self):
        fecha = self.fecha_evento_value
        descrip = self.descrip_evento_value
        if descrip:
            self.eventos_importantes_lista.append([fecha, descrip])
            self.actualizar_eventos()
        else:
            self.error("Escriba una descripción para el evento")

    def borrar_evento(self):
        current = self.eventos.currentRow()
        self.eventos_importantes_lista.pop(current)
        self.actualizar_eventos()

    def mostrar_info_evento(self):
        current = self.eventos.currentRow()
        e = self.eventos_importantes_lista[current]
        self.fecha_evento_value = e[0]
        self.descrip_evento_value = e[1]

    def ordenar_eventos(self):
        self.eventos_importantes_lista = sorted(self.eventos_importantes_lista, key=lambda i: i[0])

    # CANCIOES
    def actualizar_canciones(self):
        self.canciones.clear()
        self.ordenar_canciones()
        for cancion in self.canciones_importantes_lista:
            txt = f"{cancion[0]} {cancion[1]}"
            self.canciones.addItem(txt)

    def anadir_cancion(self):
        fecha = self.fecha_cancion_value
        descrip = self.descrip_cancion_value
        if descrip:
            self.canciones_importantes_lista.append([fecha, descrip])
            self.actualizar_canciones()
        else:
            self.error("Escriba una descripción para el cancion")

    def borrar_cancion(self):
        current = self.canciones.currentRow()
        self.canciones_importantes_lista.pop(current)
        self.actualizar_canciones()

    def mostrar_info_cancion(self):
        current = self.canciones.currentRow()
        e = self.canciones_importantes_lista[current]
        self.fecha_cancion_value = e[0]
        self.descrip_cancion_value = e[1]

    def ordenar_canciones(self):
        self.canciones_importantes_lista = sorted(self.canciones_importantes_lista, key=lambda i: i[0])

    # PERSISTENCIA DE DATOS
    def guardar_config(self):
        #try:
        with open("config.data", "wb") as  f:
            config = {"cruce_intereses":self.cruce_intereses_value, "cita":self.primera_cita_value, "beso":self.primer_beso_value, "delicioso":self.primera_vez_value, "cumple":self.birthday_value}
            pickle.dump(config, f)
        with open("eventos.saves", "wb") as  f:
            pickle.dump(self.eventos_importantes_lista, f)
        with open("canciones.saves", "wb") as  f:
            pickle.dump(self.canciones_dedicadas, f)
        #except Exception as e:
            #self.error("Guardando datos: " + e.args[0])

    def cargar_config(self):
        #try:
        config = cargar_datos_importantes()
        self.cruce_intereses_value = config["cruce_intereses"]
        self.primera_cita_value = config["cita"]
        self.primer_beso_value = config["beso"]
        self.primera_vez_value = config["delicioso"]
        self.birthday_value = config["cumple"]
        if os.path.isfile("eventos.saves"):
            with open("eventos.saves", "rb") as f:
                self.eventos_importantes_lista = pickle.load(f)
                self.ordenar_eventos()
        if os.path.isfile("canciones.saves"):
            with open("canciones.saves", "rb") as f:
                self.canciones_dedicadas = pickle.load(f)
                self.ordenar_canciones()
        self.init()
        #except Exception as e:
            #self.error("Cargando datos: " + str(e.args[0]))

    def error(self, msg):
        QMessageBox.critical(self, "ERROR", msg)

# VENTANA ACERCA DE
class AcercaDe(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("about.ui", self)
        self.show()

# INICIADOR
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = LoversTool()
    print("Abriendo aplicación....")
    ui.show()
    app.exec()
    print("LoverTool está en ejecución")