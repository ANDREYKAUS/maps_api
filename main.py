import sys
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from config import *
from api_handler import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/main_window.ui", self)

        self.current_spn = INITIAL_SPN
        self.current_coords = None

        self.show_location(INITIAL_LOCATION)

    def show_location(self, location_name=None):
        if location_name is not None:
            location_coordinates = get_coordinates_by_address(location_name)
            self.current_coords = location_coordinates
            
        location_ll = ",".join(map(str, self.current_coords))
        spn = ",".join(map(str, self.current_spn))
        image = get_static_map_image(location_ll, spn=spn)

        image = QPixmap.fromImage(ImageQt(image))

        self.image_label.setPixmap(image)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
