from PySide2 import QtWidgets, QtGui, QtCore
import hou

class AbstractPage(QtWidgets.QWidget):
    # signal allows pages to clean up after themselves
    pageClosed = QtCore.Signal()
    pageOpened = QtCore.Signal()

    def __init__(self, name, horizontal_layout=False):
        super().__init__()
        self.name = name


        # choose layout direction
        if(horizontal_layout):
            self.main_layout = QtWidgets.QHBoxLayout()
        else:
            self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        

