from importlib import reload
import hou, logging
from PySide2 import QtWidgets, QtGui, QtCore

import garden_builder.static.resources_rc

# import navigation_buttons
import garden_builder.widgets.navigation_buttons
reload(garden_builder.widgets.navigation_buttons)
from garden_builder.widgets.navigation_buttons import NavigationButtons

import garden_builder.widgets.navigation_bar
reload(garden_builder.widgets.navigation_bar)
from garden_builder.widgets.navigation_bar import NavigationBar

import garden_builder.widgets.main_page
reload(garden_builder.widgets.main_page)
from garden_builder.widgets.main_page import MainUIFrame

import garden_builder.controllers.main_controller
reload(garden_builder.controllers.main_controller)
from garden_builder.controllers.main_controller import Controller

import garden_builder.utils.qt_style
reload(garden_builder.utils.qt_style)
from garden_builder.utils.qt_style import QT_Style


class MyPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._current_node = None
        
        self.init_logging()
        self.initUI()
        self.init_controller()
        
    def init_logging(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def initUI(self):
        # self.setStyleSheet(f"background-color: {bg_color};")
        self.background_layout = QtWidgets.QVBoxLayout()
        self.background_layout.setContentsMargins(0,0,0,0)
        background_widget = QtWidgets.QWidget()
        background_widget.setObjectName("MainBackground")
        background_widget.setStyleSheet(QT_Style.get_style_sheet())

        print("\n\n\n\n\n\n\n\n\n\n")
        header = QtWidgets.QHBoxLayout()
        self.navigation_bar = NavigationBar()
        # header.addWidget(NavigationButtons(self.navigation_bar))
        # header.addWidget(self.navigation_bar)
        self.background_layout.addLayout(header)

        self.page_container = MainUIFrame(self)
        self.background_layout.addWidget(self.page_container)

        layout = QtWidgets.QVBoxLayout()
        background_widget.setLayout(self.background_layout)
        
        
        
        layout.addWidget(background_widget)
        layout.setContentsMargins(0,0,0,0) # fill entire background

        self.setLayout(layout)
    
    def init_controller(self):
        self.controller = Controller(self._current_node, self.page_container, self.navigation_bar)


    # --- Houdini Signals ---
    # signals sent from houdini from panel changes can be handled here
    def onActivate(self, kwargs):
        print("Houdini Signal: onActivateInterface\nkwargs:", kwargs)
    
    def onDeactivate(self):
        print("Houdini Signal: onDeactivateInterface")

    def onDestroy(self):
        print("Houdini Signal: onDestroyInterface")

    def onNodePathChanged(self, node):
        print("Houdini Signal: onNodePathChanged\tnode:",node)
        self._current_node = node
        self.controller.onNodePathChanged(self._current_node)
        # self._parm_dialog.setNode(node)



        


