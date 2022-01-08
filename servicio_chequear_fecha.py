from datetime import date

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox


class Comprobar():
    def __init__(self, meta, parent):
        # clase padre
        self.parent = parent
        # dict con datos
        self.meta = meta
        # centinela de notificado
        self.notificado = [date.today(), False]
        # timer
        self.timer:QTimer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.comprobar)

    def comprobar(self):
        aniv:date = self.meta["aniversario"]
        mesiversario:date = aniv
        cumple:date = self.meta["cumple"]
        evento = False
        txt = ""
        if aniv.day == date.today().day and aniv.month == date.today().month:
            txt += "* Cumples un aniversario más de relación ¡Felicidades!"
            evento = True
        if mesiversario.day == date.today().day and aniv.month != date.today().month:
            txt += "* Cumples un mesiversario más de relación ¡Felicidades!"
            evento = True
        if cumple.day == date.today().day and cumple.month == date.today().month:
            txt += "* Tu pareja cumple años ¡Felicítala!"
            evento = True
        if evento:
            if self.notificado[0] == date.today() and not self.notificado[1]:
                self.notificado[1] = True
                QMessageBox.warning(self.parent, "Hoy es el día!", txt)