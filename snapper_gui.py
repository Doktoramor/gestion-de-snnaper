#!/usr/bin/env python3
import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QLabel, QTextEdit, QMessageBox, QInputDialog
)


class SnapperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.profile = "root"
        self.setWindowTitle("Gestión de Snapshots (Snapper)")
        self.setGeometry(300, 200, 500, 400)

        self.layout = QVBoxLayout()

        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.layout.addWidget(self.log_output)

        self.btn_ver = QPushButton("Ver Instantáneas", self)
        self.btn_ver.clicked.connect(self.ver_instantaneas)
        self.layout.addWidget(self.btn_ver)

        self.btn_crear = QPushButton("Crear Nueva Instantánea", self)
        self.btn_crear.clicked.connect(self.crear_instantanea)
        self.layout.addWidget(self.btn_crear)

        self.btn_restaurar = QPushButton("Restaurar Instantánea", self)
        self.btn_restaurar.clicked.connect(self.restaurar_instantanea)
        self.layout.addWidget(self.btn_restaurar)

        self.btn_salir = QPushButton("Salir", self)
        self.btn_salir.clicked.connect(self.close)
        self.layout.addWidget(self.btn_salir)

        self.setLayout(self.layout)

    def ejecutar_comando(self, comando):
        try:
            resultado = subprocess.check_output(comando, shell=True, text=True)
            return resultado
        except subprocess.CalledProcessError as e:
            return f"Error ejecutando comando: {e}"

    def ver_instantaneas(self):
        salida = self.ejecutar_comando(f'snapper -c {self.profile} list')
        self.log_output.setPlainText("Instantáneas disponibles:\n" + salida)

    def crear_instantanea(self):
        descripcion, ok = QInputDialog.getText(self, "Crear Instantánea", "Descripción:")
        if ok and descripcion:
            resultado = self.ejecutar_comando(f'snapper -c {self.profile} create --description "{descripcion}"')
            self.log_output.setPlainText(f"Instantánea creada con descripción: {descripcion}\n{resultado}")
        else:
            QMessageBox.information(self, "Info", "No se proporcionó ninguna descripción.")

    def restaurar_instantanea(self):
        salida = self.ejecutar_comando(f'snapper -c {self.profile} list')
        self.log_output.setPlainText("Instantáneas disponibles:\n" + salida)
        id_snap, ok = QInputDialog.getText(self, "Restaurar Instantánea", "Introduce el ID de la instantánea:")
        if not ok or not id_snap.strip():
            QMessageBox.information(self, "Cancelado", "Restauración cancelada.")
            return

        confirmar = QMessageBox.question(
            self,
            "Confirmar Restauración",
            f"¿Estás seguro de que deseas restaurar la instantánea {id_snap}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmar == QMessageBox.Yes:
            resultado = self.ejecutar_comando(f'snapper -c {self.profile} undochange {id_snap}')
            self.log_output.setPlainText(f"Instantánea {id_snap} restaurada.\n{resultado}")
        else:
            QMessageBox.information(self, "Cancelado", "Restauración cancelada.")


def verificar_root():
    return os.geteuid() == 0


if __name__ == "__main__":
    if not verificar_root():
        print("Este programa debe ejecutarse como root. Usa: sudo python3 nombre_script.py")
        sys.exit(1)

    app = QApplication(sys.argv)
    ventana = SnapperApp()
    ventana.show()
    sys.exit(app.exec_())
