import sys
import time
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from api_handler import *

MAP_STYLES = {
    'Схема': "map",
    'Спутник': "sat",
    'Гибрид': "sat,skl"
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/main_window.ui", self)

        self.initial_location = 'Красноярск, Дубровинского 1И'

        self.current_zoom = 17
        self.current_coords = [0, 0]
        self.current_style = "map"
        self.placemark_coords = None
        self.is_showing_index = False

        self.init_ui()
        self.show_location((self.initial_location, False))
        self.setFocus()

    def init_ui(self):
        self.search_button.clicked.connect(self.handle_search)
        self.style_combobox.addItems(list(MAP_STYLES.keys()))
        self.style_combobox.activated[str].connect(self.handle_style_change)
        self.reset_button.clicked.connect(self.handle_reset)
        self.end_button.clicked.connect(self.new_main_address)
        self.index_checkbox.stateChanged.connect(self.handle_checkbox)

    def show_location(self, location=None):
        if location is not None:
            location_name, is_placemark = location
            toponym = get_object_by_address(location_name)
            if not toponym:
                self.statusbar.showMessage("Нет такого объекта")
                self.statusbar.setStyleSheet("background-color: red")
                return
            location_coordinates = list(get_coordinates_from_object(toponym))
            address = toponym['metaDataProperty']['GeocoderMetaData']['text']
            index = toponym['metaDataProperty']['GeocoderMetaData']['Address'].get('postal_code', "")
            address_text = address
            if self.is_showing_index and index:
                address_text += f" ({index})"
            self.address_label.setText(address_text)
            self.current_coords = location_coordinates
            if is_placemark:
                self.placemark_coords = location_coordinates.copy()
        
        location_ll = ",".join(map(str, self.current_coords))
        placemark_ll = ",".join(map(str, self.placemark_coords)) if self.placemark_coords else None
        image = get_static_map_image(location_ll, mode=self.current_style, zoom=self.current_zoom,
                                     points=[(placemark_ll, "pm2rdm")] if placemark_ll else None)

        self.status_bar()
        image = QImage.fromData(image)
        image = QPixmap.fromImage(image)

        self.image_label.setPixmap(image)

        self.statusbar.showMessage("")
        self.statusbar.setStyleSheet("")

    def status_bar(self):
        for i in range(101):
            time.sleep(0.001)
            self.status.setValue(i)

    def handle_reset(self):
        self.placemark_coords = None
        self.show_location((self.initial_location, False))

    def new_main_address(self):
        self.initial_location = self.address_input.text()
        self.show_location((self.initial_location, False))
        self.address_label.setText("")

    def handle_search(self):
        search_location = self.search_input.text()

        if not search_location.strip():
            self.statusbar.showMessage("Нет критерия поиска!")
            self.statusbar.setStyleSheet("background-color: red")
            return

        self.show_location((search_location, True))

    def handle_checkbox(self, state):
        self.is_showing_index = bool(state)
        print(self.is_showing_index)
        self.show_location()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            # self.current_spn = [self.current_spn[0] + 0.005, self.current_spn[1] + 0.005]
            self.current_zoom -= 1
            if self.current_zoom == 3:
                self.current_zoom = 4
            print(self.current_zoom)
        elif event.key() == Qt.Key_PageDown:
            # self.current_spn = [self.current_spn[0] - 0.005, self.current_spn[1] - 0.005]
            self.current_zoom += 1
            if self.current_zoom == 17:
                self.current_zoom = 16
        elif event.key() == Qt.Key_Up:
            self.current_coords[1] += 0.001 * 2 ** (17 - self.current_zoom)
        elif event.key() == Qt.Key_Down:
            self.current_coords[1] -= 0.001 * 2 ** (17 - self.current_zoom)
        elif event.key() == Qt.Key_Left:
            self.current_coords[0] -= 0.001 * 2 ** (17 - self.current_zoom)
        elif event.key() == Qt.Key_Right:
            self.current_coords[0] += 0.001 * 2 ** (17 - self.current_zoom)
        elif event.key() == Qt.Key_Escape:
            self.close()

        if event.key() in [Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Up, Qt.Key_Down,
                           Qt.Key_Left, Qt.Key_Right]:
            self.show_location()

    def handle_style_change(self, text):
        self.current_style = MAP_STYLES[text]
        self.show_location()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            position = event.pos()
            x = event.x() - 80
            y = event.y() - 80

            if x > 650 or y > 450:
                return
            
            self.placemark_coords = screen_to_geo(*self.current_coords, x, y, self.current_zoom)
            placemark_ll = ",".join([str(element) for element in self.placemark_coords])

            toponym = get_object_by_address(placemark_ll)

            address = toponym['metaDataProperty']['GeocoderMetaData']['text'] + " "

            closest_org = find_closest_organization(address, placemark_ll)

            if self.is_showing_index:
                address_object = toponym['metaDataProperty']['GeocoderMetaData']['Address']
                if 'postal_code' in address_object:
                    index = address_object['postal_code']
                    address += index + " "

            if closest_org:
                org_name = closest_org['properties']['CompanyMetaData']['name']
                address += f"(ближайшая организация: {org_name})"

            self.address_label.setText(address)
            self.show_location()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
