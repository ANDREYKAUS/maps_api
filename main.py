import sys
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from api_handler import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/main_window.ui", self)

        initial_location = "Красноярск, Дубровинского 1И"

        self.current_spn = [0.005, 0.005]
        self.current_coords = [0, 0]

        self.show_location(initial_location)
        self.init_ui()
        self.setFocus()

    def init_ui(self):
        self.search_button.clicked.connect(self.handle_search)

    def show_location(self, location_name=None):
        if location_name is not None:
            location_coordinates = list(get_coordinates_by_address(location_name))
            self.current_coords = location_coordinates
            
        location_ll = ",".join(map(str, self.current_coords))
        spn = ",".join(map(str, self.current_spn))
        image = get_static_map_image(location_ll, spn=spn)

        image = QPixmap.fromImage(ImageQt(image))

        self.image_label.setPixmap(image)

    def handle_search(self):
        search_location = self.search_input.text()
        
        self.show_location(search_location)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.current_spn = [self.current_spn[0] + 0.005, self.current_spn[1] + 0.005]
        elif event.key() == Qt.Key_PageDown:
            self.current_spn = [self.current_spn[0] - 0.005, self.current_spn[1] - 0.005]
        elif event.key() == Qt.Key_Up:
            self.current_coords[1] += 0.001
        elif event.key() == Qt.Key_Down:
            self.current_coords[1] -= 0.001
        elif event.key() == Qt.Key_Left:
            self.current_coords[0] -= 0.001
        elif event.key() == Qt.Key_Right:
            self.current_coords[0] += 0.001
        elif event.key() == Qt.Key_Escape:
            self.close()

        if event.key() in [Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Up, Qt.Key_Down,
                           Qt.Key_Left, Qt.Key_Right]:
            self.show_location()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
