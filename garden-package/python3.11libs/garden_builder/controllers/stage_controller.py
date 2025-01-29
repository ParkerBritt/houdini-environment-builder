from PySide2 import QtWidgets, QtGui, QtCore
from importlib import reload
import os, hou

import garden_builder.viewer_states.state_mode
reload(garden_builder.viewer_states.state_mode)
from garden_builder.viewer_states.state_mode import ViewerMode

class StageController():
    def __init__(self, main_controller, page_container):
        """Control the functionality of the stage page"""
        self.node = None
        self.main_controller = main_controller
        self.page_container = page_container
        self.stage_page = page_container.stage_page

    def connect_signals(self):
        """Connect qt signals to appropriate slots."""
        self.stage_page.pageOpened.connect(self.on_page_opened)
        self.stage_page.enter_network_bttn.clicked.connect(self.on_enter_network_button_clicked)

    def on_enter_network_button_clicked(self):
        self.node.node("RENDER/user_edit").children()[0].setCurrent(True)
        
    def on_page_opened(self):
        if(not self.node):
            return

        # reset state
        self.node.parm("state_mode").set(ViewerMode.map_state(ViewerMode.INACTIVE))

    def onNodePathChanged(self, node):
        """Refetch plant registry when node path changes."""
        self.node = node
        if(not self.node):
            return

        material_interface_node = self.node.node("RENDER/material_registry")
        self.stage_page.material_parm_dialog.setNode(material_interface_node)
