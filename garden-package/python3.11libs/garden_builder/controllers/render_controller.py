from PySide2 import QtWidgets, QtGui, QtCore
from importlib import reload
import os, hou

import garden_builder.viewer_states.state_mode
reload(garden_builder.viewer_states.state_mode)
from garden_builder.viewer_states.state_mode import ViewerMode

class RenderController():
    def __init__(self, main_controller, page_container):
        """Control the functionality of the render page"""
        self.node = None
        self.main_controller = main_controller
        self.page_container = page_container
        self.render_page = page_container.render_page

    def connect_signals(self):
        """Connect qt signals to appropriate slots."""
        self.render_page.pageOpened.connect(self.on_page_opened)
        self.render_page.render_button.clicked.connect(self.on_render_clicked)
        self.render_page.render_mplay_button.clicked.connect(self.on_render_mplay_clicked)

    def on_render_clicked(self):
        print("rendering")
        hou.ui.displayMessage("Render started")
        self.node.parm("RENDER/render_rop/execute").pressButton()

    def on_render_mplay_clicked(self):
        print("rendering")
        self.node.parm("RENDER/render_rop/renderpreview").pressButton()
        
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

        render_interface_node = self.node.node("RENDER/render_settings_interface")
        self.render_page.render_settings_parm_dialog.setNode(render_interface_node)
