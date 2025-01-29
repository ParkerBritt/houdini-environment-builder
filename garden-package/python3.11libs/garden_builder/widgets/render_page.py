from PySide2 import QtWidgets, QtGui, QtCore
import hou
import os

from importlib import reload

import garden_builder.widgets.abstract_page
reload(garden_builder.widgets.abstract_page)
from garden_builder.widgets.abstract_page import AbstractPage

class RenderPage(AbstractPage):
    def __init__(self):
        super().__init__("Render")
        self.registry_stretch=0.8

        self.thumbnail_text = ""

        self.initUI()


    def init_render_settings(self):
        # layout
        self.render_settings_w = QtWidgets.QWidget()
        self.render_settings_l = QtWidgets.QVBoxLayout()
        self.render_settings_w.setProperty("dark_background", True)
        self.render_settings_w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.render_settings_w.setLayout(self.render_settings_l)
        self.render_settings_w.setContentsMargins(0,10,0,0)

        self.render_settings_container_l.addWidget(self.render_settings_w)

        # title
        title = QtWidgets.QLabel("Render Settings")
        title.setProperty("transparent_background", True)
        title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        title_font = title.font()
        title_font.setPointSize(13)
        title.setFont(title_font)
        self.render_settings_l.addWidget(title)

        # parm dialog
        self.render_settings_parm_dialog = hou.qt.ParmDialog(None)
        self.render_settings_parm_dialog.setProperty("transparent_background", True)
        self.render_settings_parm_dialog.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.render_settings_l.addWidget(self.render_settings_parm_dialog)


    def initUI(self):
        self.contents_l = QtWidgets.QHBoxLayout()
        self.title_l = QtWidgets.QHBoxLayout()
    
        self.main_layout.addLayout(self.title_l)
        self.main_layout.addLayout(self.contents_l)

        self.render_settings_container_w = QtWidgets.QWidget()
        self.render_settings_container_l = QtWidgets.QVBoxLayout()
        self.render_settings_container_l.setContentsMargins(0,0,0,0)
        self.render_settings_container_w.setLayout(self.render_settings_container_l)
        self.contents_l.addWidget(self.render_settings_container_w, stretch=6)


        self.init_title()
        self.init_render_settings()

        # button
        self.render_buttons_l = QtWidgets.QHBoxLayout()
        self.render_button = QtWidgets.QPushButton("Render")
        self.render_mplay_button = QtWidgets.QPushButton("Render Preview")
        self.render_buttons_l.addWidget(self.render_button)
        self.render_buttons_l.addWidget(self.render_mplay_button)
        self.render_settings_container_l.addLayout(self.render_buttons_l)

    def init_title(self):
        self.title_l.addWidget(title := QtWidgets.QLabel("Render"))
        self.title_l.setAlignment(QtCore.Qt.AlignTop)
        title_font = title.font()
        title_font.setPointSize(25)
        title.setFont(title_font)
        self.title_l.addStretch()
