import sys
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from api_handler import *

MAP_STYLES = {
    'Схема': "map",
    'Спутник': "sat",
    'Гибрид': "sat, skl"
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/main_window.ui", self)

        initial_location = "Красноярск, Дубровинского 1И"

        self.current_spn = [0.005, 0.005]
        self.current_coords = [0, 0]
        self.current_style = "map"
        self.placemark_coords = None

        self.init_ui()
        self.show_location((initial_location, False))
        self.setFocus()

    def init_ui(self):
        self.search_button.clicked.connect(self.handle_search)
        self.style_combobox.addItems(list(MAP_STYLES.keys()))
        self.style_combobox.activated[str].connect(self.handle_style_change)
        self.reset_button.clicked.connect(self.reset_mode)

    def show_location(self, location=None):
        if location is not None:
            location_name, is_placemark = location
            location_coordinates = list(get_coordinates_by_address(location_name))
            self.current_coords = location_coordinates
            if is_placemark:
                self.placemark_coords = location_coordinates.copy()
        
        location_ll = ",".join(map(str, self.current_coords))
        placemark_ll = ",".join(map(str, self.placemark_coords)) if self.placemark_coords else None
        print(placemark_ll)
        spn = ",".join(map(str, self.current_spn))
        image = get_static_map_image(location_ll, mode=self.current_style, spn=spn,
                                     points=[(placemark_ll, "pm2rdm")] if placemark_ll else None)

        image = QImage.fromData(image)
        image = QPixmap.fromImage(image)

        self.image_label.setPixmap(image)

    def reset_mode(self):
        self.show_location('Красноярск, Дубровинского 1И"')

    def handle_search(self):
        search_location = self.search_input.text()
        
        self.show_location((search_location, True))

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

    def handle_style_change(self, text):
        self.current_style = MAP_STYLES[text]
        self.show_location()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
