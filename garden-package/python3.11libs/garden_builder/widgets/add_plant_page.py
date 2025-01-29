from PySide2 import QtWidgets, QtGui, QtCore
import hou
import os

from importlib import reload

import garden_builder.widgets.abstract_page
reload(garden_builder.widgets.abstract_page)
from garden_builder.widgets.abstract_page import AbstractPage

class PathSelector(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.main_l = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_l)
        self.main_l.setContentsMargins(0,0,0,0)
        self.line_w = QtWidgets.QLineEdit()
        self.bttn_w = QtWidgets.QPushButton()
        self.bttn_w.setFixedSize(25, 25)
        self.bttn_w.setProperty("mid_background", True)

        self.main_l.addWidget(self.line_w)
        self.main_l.addWidget(self.bttn_w)

    def clear(self):
        self.line_w.clear()

    def text(self):
        return self.line_w.text()


class FileSelector(PathSelector):
    def __init__(self):
        super().__init__()
        self.bttn_w.clicked.connect(self.onButtonPressed)
        self.bttn_w.setIcon(QtGui.QIcon(":images/icons/file_8x.png"))
    def onButtonPressed(self):
        selected_file_path = hou.ui.selectFile() 
        if(not selected_file_path):
            return
        selected_file_path = os.path.expandvars(selected_file_path)
        self.line_w.setText(selected_file_path)

class NodeSelector(PathSelector):
    def __init__(self):
        super().__init__()
        self.bttn_w.clicked.connect(self.onButtonPressed)
        self.bttn_w.setIcon(QtGui.QIcon(":images/icons/node_8x.png"))
    def onButtonPressed(self):
        selected_node_path = hou.ui.selectNode(node_type_filter=hou.nodeTypeFilter.Sop) 
        if(not selected_node_path):
            return
        self.line_w.setText(selected_node_path)


class SettingsForm(QtWidgets.QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        self.name_w = QtWidgets.QLineEdit()

        self.method_w = QtWidgets.QComboBox()
        self.method_w.addItem("File")
        self.method_w.addItem("Sop")
        self.method_w.addItem("Procedural")

        self.template_w = QtWidgets.QComboBox()
        self.template_w.addItem("Bamboo")
        self.template_w.addItem("Lilypad")
        self.template_w.addItem("Black Pine")
        self.template_w.addItem("Fern")
        self.template_w.addItem("Rock")

        self.proxy_file_w = FileSelector()
        self.render_file_w = FileSelector()
        self.proxy_node_w = NodeSelector()
        self.render_node_w = NodeSelector()
        self.auto_proxy_w = QtWidgets.QCheckBox()
        self.auto_proxy_w.setProperty("transparent_background", True)

        # TODO: add sop and file path selectors
        # try to use build in houdini scripts to get the file dialog
        self.addRow("Name", self.name_w)
        self.addRow("Method", self.method_w)
        self.render_node_row_w = self.addRow("Render Geo", self.render_node_w)
        self.render_file_row_w = self.addRow("Render Geo", self.render_file_w)
        self.auto_proxy_row_w = self.addRow("Auto Proxy", self.auto_proxy_w)
        self.proxy_file_row_w = self.addRow("Proxy Geo", self.proxy_file_w)
        self.proxy_node_row_w = self.addRow("Proxy Geo", self.proxy_node_w)
        self.template_row_w = self.addRow("Template", self.template_w)

    def addRow(self, label_text, item=None):
        label = QtWidgets.QLabel(label_text)

        label.setProperty("transparent_background", True)
        new_item_l = QtWidgets.QVBoxLayout()
        new_item_l.addWidget(label)
        new_item_l.addWidget(item)
        new_item_l.setContentsMargins(0,0,0,0)

        new_item_w = QtWidgets.QWidget()
        new_item_w.setLayout(new_item_l)
        new_item_w.setProperty("transparent_background", True)

        self.addWidget(new_item_w)

        return new_item_w
    
    def clear(self):
        self.name_w.clear()
        self.method_w.setCurrentText("File")
        self.method_w.currentTextChanged.emit("File")
        self.proxy_file_w.clear()
        self.render_file_w.clear()
        self.proxy_node_w.clear()
        self.render_node_w.clear()
        self.auto_proxy_w.setChecked(True)



        

class AddPlantPage(AbstractPage):
    def __init__(self):
        super().__init__("Add Plant")

        self.initUI()
        self.init_settings_UI()
        self.init_controls_UI()


    def initUI(self):
        title_l = QtWidgets.QVBoxLayout()
        self.title_w = QtWidgets.QLabel("Add Plant")
        title_font = self.title_w.font()
        title_font.setPointSize(25)
        self.title_w.setFont(title_font)
        title_l.addWidget(self.title_w)
        self.main_layout.addWidget(self.title_w)

        self.content_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)

    def init_settings_UI(self):
        # setup
        self.settings_layout = QtWidgets.QVBoxLayout()
        self.content_layout.addLayout(self.settings_layout, stretch=8)
        background_w = QtWidgets.QWidget() 
        background_w.setProperty("dark_background", True)
        self.settings_layout.addWidget(background_w)
        background_l = QtWidgets.QVBoxLayout()
        background_l.setAlignment(QtCore.Qt.AlignTop)
        background_w.setLayout(background_l)
        background_w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # title
        background_l.addWidget(title_w := QtWidgets.QLabel("Settings"))
        title_font = self.title_w.font()
        title_font.setPointSize(15)
        title_w.setFont(title_font)
        title_w.setAlignment(QtCore.Qt.AlignCenter)

        # form
        self.settings_form_l = SettingsForm()
        self.settings_form_l.setSpacing(10)
        background_l.addLayout(self.settings_form_l)


        # bottom buttons
        background_l.addStretch()
        button_l = QtWidgets.QHBoxLayout()
        background_l.addLayout(button_l)
        button_l.addStretch()
        self.cancel_bttn_w = QtWidgets.QPushButton("cancel")
        self.cancel_bttn_w.setProperty("mid_background", True)
        self.done_bttn_w = QtWidgets.QPushButton("done")
        self.done_bttn_w.setProperty("mid_background", True)
        button_l.addWidget(self.cancel_bttn_w)
        button_l.addWidget(self.done_bttn_w)

    def init_controls_UI(self):
        # setup
        self.controls_layout = QtWidgets.QVBoxLayout()
        self.content_layout.addLayout(self.controls_layout, stretch=10)
        background_w = QtWidgets.QWidget() 
        background_w.setProperty("dark_background", True)
        self.controls_layout.addWidget(background_w)
        background_l = QtWidgets.QVBoxLayout()
        background_l.setAlignment(QtCore.Qt.AlignTop)
        background_w.setLayout(background_l)
        background_w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        


        # title
        background_l.addWidget(title_w := QtWidgets.QLabel("Controls"))
        title_font = self.title_w.font()
        title_font.setPointSize(15)
        title_w.setFont(title_font)
        title_w.setAlignment(QtCore.Qt.AlignCenter)

        self.parm_dialog = hou.qt.ParmDialog(None)
        self.parm_dialog.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.parm_dialog.setProperty("transparent_background", True)
        background_l.addWidget(self.parm_dialog)
