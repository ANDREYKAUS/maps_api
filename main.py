import sys
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from api_handler import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/main_window.ui", self)

        initial_location = "Красноярск, Дубровинского 1И"

        self.current_spn = [0.005, 0.005]
        self.current_coords = [0, 0]
        self.current_style = 'map'

        self.change_l()
        self.show_location(initial_location)
        self.setFocus()

    def show_location(self, location_name=None):
        if location_name is not None:
            location_coordinates = list(get_coordinates_by_address(location_name))
            self.current_coords = location_coordinates
            
        location_ll = ",".join(map(str, self.current_coords))
        spn = ",".join(map(str, self.current_spn))
        image = get_static_map_image(location_ll, mode=self.current_style, spn=spn)

        image = QImage.fromData(image)
        image = QPixmap.fromImage(image)

        self.image_label.setPixmap(image)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.current_coords[1] += 0.001
            self.show_location()
        elif event.key() == Qt.Key_Down:
            self.current_coords[1] -= 0.001
            self.show_location()
        elif event.key() == Qt.Key_Left:
            self.current_coords[0] -= 0.001
            self.show_location()
        elif event.key() == Qt.Key_Right:
            self.current_coords[0] += 0.001
            self.show_location()
        elif event.key() == Qt.Key_Escape:
            self.close()

    def change_l(self):
        combo = self.SNPbox
        combo.addItems(["map", "sat", "sat,skl"])
        combo.activated[str].connect(self.onActivated)

    def onActivated(self, text):
        self.current_style = text
        self.show_location()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
