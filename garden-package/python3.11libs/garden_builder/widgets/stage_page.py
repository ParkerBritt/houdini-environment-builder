from PySide2 import QtWidgets, QtGui, QtCore
import hou
import os

from importlib import reload

import garden_builder.widgets.abstract_page
reload(garden_builder.widgets.abstract_page)
from garden_builder.widgets.abstract_page import AbstractPage

class StagePage(AbstractPage):
    def __init__(self):
        super().__init__("Stage")
        self.registry_stretch=0.8

        self.thumbnail_text = ""

        self.initUI()

    def init_material_assign(self):
        # layout
        self.materials_w = QtWidgets.QWidget()
        self.materials_l = QtWidgets.QVBoxLayout()
        self.materials_l.setContentsMargins(0,10,0,0)
        self.materials_w.setProperty("dark_background", True)
        self.materials_w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.materials_w.setLayout(self.materials_l)
        self.materials_container_l.addWidget(self.materials_w)

        # title
        title = QtWidgets.QLabel("Assign Materials")
        title.setProperty("transparent_background", True)
        title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        title_font = title.font()
        title_font.setPointSize(13)
        title.setFont(title_font)
        self.materials_l.addWidget(title)

        # parm dialog
        self.material_parm_dialog = hou.qt.ParmDialog(None)
        self.material_parm_dialog.setProperty("transparent_background", True)
        self.material_parm_dialog.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.materials_l.addWidget(self.material_parm_dialog)



    def initUI(self):
        self.contents_l = QtWidgets.QHBoxLayout()
        self.title_l = QtWidgets.QHBoxLayout()
    
        self.main_layout.addLayout(self.title_l)
        self.main_layout.addLayout(self.contents_l)

        self.materials_container_w = QtWidgets.QWidget()
        self.materials_container_l = QtWidgets.QVBoxLayout()
        self.materials_container_l.setContentsMargins(0,0,0,0)
        self.materials_container_w.setLayout(self.materials_container_l)
        self.contents_l.addWidget(self.materials_container_w, stretch=4)

        self.init_title()
        self.init_material_assign()

        # button
        self.enter_network_bttn = QtWidgets.QPushButton("Edit Network")
        self.materials_container_l.addWidget(self.enter_network_bttn)

    def init_title(self):
        self.title_l.addWidget(title := QtWidgets.QLabel("Stage"))
        self.title_l.setAlignment(QtCore.Qt.AlignTop)
        title_font = title.font()
        title_font.setPointSize(25)
        title.setFont(title_font)
        self.title_l.addStretch()
