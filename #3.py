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