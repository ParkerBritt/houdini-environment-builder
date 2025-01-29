from PySide2 import QtWidgets, QtGui, QtCore
from importlib import reload
import os, hou

import garden_builder.viewer_states.state_mode
reload(garden_builder.viewer_states.state_mode)
from garden_builder.viewer_states.state_mode import ViewerMode

class TerrainController():
    def __init__(self, main_controller, page_container):
        """Control the functionality of the terrain page"""
        self.node = None
        self.main_controller = main_controller
        self.page_container = page_container
        self.terrain_page = page_container.terrain_page

    def connect_signals(self):
        """Connect qt signals to appropriate slots."""
        self.terrain_page.mode_bttn_grp.buttonClicked.connect(self.on_mode_bttn_clicked)
        self.terrain_page.pageOpened.connect(self.on_page_opened)
        self.terrain_page.pageClosed.connect(self.on_page_closed)

    def onNodePathChanged(self, node):
        """Refetch plant registry when node path changes."""
        self.node = node
        self.terrain_page.terrain_settings_parm_dialog.setNode(self.node.node("init_terrain/heightfield_interface"))

    def on_page_opened(self):
        if(not self.node):
            return
        self.node.setOutputForViewFlag(1)

        # reset state
        self.node.parm("state_mode").set(ViewerMode.map_state(ViewerMode.INACTIVE))

        # uncheck button
        checked_button = self.terrain_page.mode_bttn_grp.checkedButton()
        if(checked_button is not None):
            self.terrain_page.mode_bttn_grp.setExclusive(False)
            checked_button.setChecked(False)
            self.terrain_page.mode_bttn_grp.setExclusive(True)

    def on_page_closed(self):
        if not self.node:
            return

        # set preview mode to default
        print("setting mode")
        preview_mode_parm = self.node.parm("preview_mode")
        preview_mode_parm.set("plants")


    def on_mode_bttn_clicked(self, button):
        """Change plant distribution mode."""

        parm = self.node.parm("state_mode")
        parm.set(ViewerMode.map_state(button.token))
        parm.pressButton()

        preview_mode_parm = self.node.parm("preview_mode")

        if(button.token in (ViewerMode.WATER_CURVE, ViewerMode.WATER_REGION, ViewerMode.WATER_DELETE)):
            preview_mode_parm.set("water")
        elif(button.token in (ViewerMode.TERRAIN_DRAW, ViewerMode.TERRAIN_SELECT, ViewerMode.TERRAIN_DELETE)):
            preview_mode_parm.set("terrain")

        # interface_mapping = {
        #     "point":"distribution_operations/place_point_operation/interface",
        #     "draw":"distribution_operations/draw_region_operation/interface",
        #     "edit":"distribution_operations/edit_operation/interface",
        #     "delete":"distribution_operations/delete_interface"
        # }
        # print("switching to:", interface_mapping[button.token])
        # self.plants_page.parm_dialog.setNode(self.node.node(interface_mapping[button.token]))

