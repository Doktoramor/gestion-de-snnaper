from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QDialog, QDialogButtonBox, QMessageBox
import sys
import subprocess

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Snapshots")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        # Botón para ver instantáneas
        self.ver_btn = QPushButton("Ver Instantáneas", self)
        self.ver_btn.clicked.connect(self.ver_instantaneas)
        self.layout.addWidget(self.ver_btn)

        # Botón para crear instantánea
        self.crear_btn = QPushButton("Crear Instantánea", self)
        self.crear_btn.clicked.connect(self.crear_instantanea)
        self.layout.addWidget(self.crear_btn)

        # Botón para restaurar instantánea
        self.restaurar_btn = QPushButton("Restaurar Instantánea", self)
        self.restaurar_btn.clicked.connect(self.restaurar_instantanea)
        self.layout.addWidget(self.restaurar_btn)

        # Botón para salir
        self.salir_btn = QPushButton("Salir", self)
        self.salir_btn.clicked.connect(self.close)
        self.layout.addWidget(self.salir_btn)

        self.setLayout(self.layout)

    # Método para ver las instantáneas
    def ver_instantaneas(self):
        # Aquí se listarán las instantáneas usando snapper
        try:
            result = subprocess.run(["snapper", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                QMessageBox.information(self, "Instantáneas", result.stdout.decode())
            else:
                QMessageBox.warning(self, "Error", "No se pudieron obtener las instantáneas.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error al obtener las instantáneas: {str(e)}")

    # Método para crear una nueva instantánea
    def crear_instantanea(self):
        # Ventana emergente para introducir la descripción de la instantánea
        dialog = CrearInstantaneaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            descripcion = dialog.descripcion_input.text()
            if descripcion:
                try:
                    subprocess.run(["snapper", "create", "--description", descripcion], check=True)
                    QMessageBox.information(self, "Creación de Instantánea", f"Instantánea creada con descripción: {descripcion}")
                except subprocess.CalledProcessError:
                    QMessageBox.warning(self, "Error", "Hubo un error al crear la instantánea.")
            else:
                QMessageBox.warning(self, "Descripción Vacía", "No se proporcionó ninguna descripción.")

    # Método para restaurar una instantánea
    def restaurar_instantanea(self):
        # Mostrar instantáneas disponibles para restaurar
        try:
            result = subprocess.run(["snapper", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                instantaneas = result.stdout.decode().splitlines()
                if not instantaneas:
                    QMessageBox.warning(self, "No hay Instantáneas", "No se encontraron instantáneas para restaurar.")
                    return
                # Seleccionar la instantánea a restaurar
                id_instantanea, _ = self.seleccionar_instantanea(instantaneas)
                if id_instantanea:
                    # Confirmación antes de restaurar
                    confirm = QMessageBox.question(self, "Confirmación", f"¿Deseas restaurar la instantánea {id_instantanea}?", QMessageBox.Yes | QMessageBox.No)
                    if confirm == QMessageBox.Yes:
                        subprocess.run(["snapper", "undochange", id_instantanea])
                        QMessageBox.information(self, "Restauración", f"Instantánea {id_instantanea} restaurada.")
            else:
                QMessageBox.warning(self, "Error", "No se pudieron obtener las instantáneas.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error al intentar restaurar la instantánea: {str(e)}")

    def seleccionar_instantanea(self, instantaneas):
        # Crear una ventana de selección para elegir la instantánea a restaurar
        dialog = QDialog(self)
        dialog.setWindowTitle("Seleccionar Instantánea")
        layout = QVBoxLayout(dialog)

        for instantanea in instantaneas:
            btn = QPushButton(instantanea, dialog)
            btn.clicked.connect(dialog.accept)
            layout.addWidget(btn)

        dialog.setLayout(layout)
        dialog.exec_()
        selected_button = dialog.selectedButton()
        if selected_button:
            return selected_button.text().split()[0], selected_button.text()  # Devuelve el ID de la instantánea
        return None, None

# Diálogo para la creación de una instantánea
class CrearInstantaneaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Instantánea")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout(self)

        self.descripcion_label = QLabel("Descripción de la Instantánea:", self)
        layout.addWidget(self.descripcion_label)

        self.descripcion_input = QLineEdit(self)
        layout.addWidget(self.descripcion_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
