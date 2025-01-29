from PySide2 import QtWidgets, QtGui, QtCore
import hou, os

from importlib import reload

import garden_builder.widgets.abstract_page
reload(garden_builder.widgets.abstract_page)
from garden_builder.widgets.abstract_page import AbstractPage

import garden_builder.widgets.dist_button
reload(garden_builder.widgets.dist_button)
from garden_builder.widgets.dist_button import DistButton

import garden_builder.viewer_states.state_mode
reload(garden_builder.viewer_states.state_mode)
from garden_builder.viewer_states.state_mode import ViewerMode


class TerrainPage(AbstractPage):
    def __init__(self):
        super().__init__("Terrain")

        self.initUI()

    def initUI(self):

        self.contents_l = QtWidgets.QHBoxLayout()
        self.title_l = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.title_l)
        self.main_layout.addLayout(self.contents_l)

        self.init_title()
        self.init_contents()

    def init_contents(self):
        self.settings_container_l = QtWidgets.QVBoxLayout()
        self.modes_container_l = QtWidgets.QVBoxLayout()
        self.contents_l.addLayout(self.settings_container_l)
        self.contents_l.addLayout(self.modes_container_l)
        self.init_settings()
        self.init_modes()

    def init_settings(self):
        settings_w = QtWidgets.QWidget()
        settings_w.setProperty("dark_background", True)
        settings_w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.settings_l = QtWidgets.QVBoxLayout()
        settings_w.setLayout(self.settings_l)
        self.settings_container_l.addWidget(settings_w)
        self.settings_container_l.setContentsMargins(0,0,0,0)

        # title
        title = QtWidgets.QLabel("General Terrain Settings")
        title.setProperty("transparent_background", True)
        title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        title_font = title.font()
        title_font.setPointSize(13)
        title.setFont(title_font)
        self.settings_l.addWidget(title)

        # parm dialog
        self.terrain_settings_parm_dialog = hou.qt.ParmDialog(None, compact=True, labelsize=1.1)
        self.terrain_settings_parm_dialog.setProperty("transparent_background", True)
        self.terrain_settings_parm_dialog.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.settings_l.addWidget(self.terrain_settings_parm_dialog)

    def init_modes(self):
        modes_w = QtWidgets.QWidget()
        modes_w.setProperty("transparent_background", True)
        self.modes_container_l.addWidget(modes_w)

        modes_terrain_bg_w = QtWidgets.QWidget()
        modes_water_bg_w = QtWidgets.QWidget()
        self.modes_container_l.addWidget(modes_terrain_bg_w)
        self.modes_container_l.addWidget(modes_water_bg_w)
        modes_water_bg_w.setProperty("dark_background", True)
        modes_terrain_bg_w.setProperty("dark_background", True)
        modes_terrain_bg_w.setMinimumWidth(100)
        modes_water_bg_w.setMinimumWidth(100)
        
        self.modes_water_l = QtWidgets.QVBoxLayout()
        self.modes_terrain_l = QtWidgets.QVBoxLayout()
        modes_water_bg_w.setLayout(self.modes_water_l)
        modes_terrain_bg_w.setLayout(self.modes_terrain_l)

        modes_water_bg_w.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        modes_terrain_bg_w.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

        # add title
        water_title = QtWidgets.QLabel("Water")
        terrain_title = QtWidgets.QLabel("Terrain")
        water_title.setProperty("transparent_background", True)
        terrain_title.setProperty("transparent_background", True)
        terrain_title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        water_title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.modes_water_l.addWidget(water_title)
        self.modes_terrain_l.addWidget(terrain_title)

        self.init_buttons()

        
    def init_buttons(self):
        icons_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static/icons")
        self.terrain_draw_bttn = DistButton("Draw",os.path.join(icons_path, "dist_region.svg"), ViewerMode.TERRAIN_DRAW)
        self.terrain_adjust_bttn = DistButton("Adjust",os.path.join(icons_path, "dist_edit.svg"), ViewerMode.TERRAIN_SELECT)
        self.terrain_delete_bttn = DistButton("Delete",os.path.join(icons_path, "dist_erase.svg"), ViewerMode.TERRAIN_DELETE)

        self.modes_terrain_l.addStretch()
        self.modes_terrain_l.addWidget(self.terrain_draw_bttn)
        self.modes_terrain_l.addStretch()
        self.modes_terrain_l.addWidget(self.terrain_adjust_bttn)
        self.modes_terrain_l.addStretch()
        self.modes_terrain_l.addWidget(self.terrain_delete_bttn)
        self.modes_terrain_l.addStretch()

        self.water_river_bttn = DistButton("Draw River",os.path.join(icons_path, "dist_region.svg"), ViewerMode.WATER_CURVE)
        self.water_lake_bttn = DistButton("Draw Lake",os.path.join(icons_path, "dist_region.svg"), ViewerMode.WATER_REGION)
        self.water_delete_bttn = DistButton("Delete",os.path.join(icons_path, "dist_erase.svg"), ViewerMode.WATER_DELETE)

        self.modes_water_l.addStretch()
        self.modes_water_l.addWidget(self.water_river_bttn)
        self.modes_water_l.addStretch()
        self.modes_water_l.addWidget(self.water_lake_bttn)
        self.modes_water_l.addStretch()
        self.modes_water_l.addWidget(self.water_delete_bttn)
        self.modes_water_l.addStretch()

        self.mode_bttn_grp = QtWidgets.QButtonGroup()
        self.mode_bttn_grp.addButton(self.terrain_draw_bttn)
        self.mode_bttn_grp.addButton(self.terrain_adjust_bttn)
        self.mode_bttn_grp.addButton(self.terrain_delete_bttn)
        self.mode_bttn_grp.addButton(self.water_river_bttn)
        self.mode_bttn_grp.addButton(self.water_lake_bttn)
        self.mode_bttn_grp.addButton(self.water_delete_bttn)


    def init_title(self):
        title = QtWidgets.QLabel("Terrain Page")
        title_font = title.font()
        # title_font.setBold(True)
        title_font.setPointSize(25)
        title.setFont(title_font)
        self.title_l.setAlignment(QtCore.Qt.AlignTop)
        self.title_l.addWidget(title)

