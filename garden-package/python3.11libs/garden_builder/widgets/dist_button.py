from PySide2 import QtWidgets, QtGui, QtCore, QtSvg

class DistButton(QtWidgets.QPushButton):
    def __init__(self, text, icon, token, parent=None):
        super().__init__(parent)
        self.token = token

        self.setProperty("mid_background", True)
        self.setCheckable(True)

        self.setMinimumSize(60,60)
        self.setMaximumSize(150,150)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)

        svg_container_w = QtWidgets.QWidget(self)
        svg_container_w.setProperty("transparent_background", True)
        svg_l = QtWidgets.QVBoxLayout(svg_container_w)
        svg_l.setContentsMargins(0, 0, 0, 0)
        svg_l.setAlignment(QtCore.Qt.AlignCenter)

        self.svg_w = QtSvg.QSvgWidget(icon)
        self.svg_w.renderer().setAspectRatioMode(QtCore.Qt.KeepAspectRatio)
        self.svg_w.setProperty("transparent_background", True)
        svg_l.addWidget(self.svg_w)

        self.label_text = text
        text_lbl = QtWidgets.QLabel(text)
        text_lbl.setAlignment(QtCore.Qt.AlignCenter)
        text_lbl.setProperty("transparent_background", True)

        layout.addWidget(svg_container_w)
        layout.addWidget(text_lbl)
