from PySide2 import QtWidgets, QtGui, QtCore
import hou

class LandingPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.initUI()

    def initUI(self):

        title = QtWidgets.QLabel("Garden Builder")
        title_font = title.font()
        title_font.setBold(True)
        title_font.setPointSize(20)
        title.setFont(title_font)
        self.main_layout.addWidget(title)

        sub_title = QtWidgets.QLabel("Parker Britt")
        self.main_layout.addWidget(sub_title)

        guide_text = QtWidgets.QLabel("To start building your garden navigate to the terrain page on the left")
        self.main_layout.addWidget(guide_text)

        help_text = QtWidgets.QLabel("Need help?\nPress the help button in the bottom left corner")
        self.main_layout.addWidget(help_text)

