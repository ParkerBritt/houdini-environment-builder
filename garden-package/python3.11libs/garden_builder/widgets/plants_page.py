from PySide2 import QtWidgets, QtGui, QtCore
import hou
import os

from importlib import reload

import garden_builder.widgets.dist_button
reload(garden_builder.widgets.dist_button)
from garden_builder.widgets.dist_button import DistButton

import garden_builder.widgets.add_plant_page
reload(garden_builder.widgets.add_plant_page)
from garden_builder.widgets.add_plant_page import AddPlantPage

import garden_builder.widgets.abstract_page
reload(garden_builder.widgets.abstract_page)
from garden_builder.widgets.abstract_page import AbstractPage

import garden_builder.utils.viewer_state_utils
reload(garden_builder.utils.viewer_state_utils)
from garden_builder.utils.viewer_state_utils import state_from_node

from garden_builder.utils import qt_utils
reload(garden_builder.utils.qt_utils)


class PlantsPage(AbstractPage):
    def __init__(self):
        super().__init__("Plants")
        self.registry_stretch=0.8

        self.thumbnail_text = ""

        self.initUI()
        self.init_title()
        self.init_registry()
        self.init_distribution()
        self.resizeEvent = self.on_resize

    def initUI(self):

        self.contents_l = QtWidgets.QHBoxLayout()
        self.title_l = QtWidgets.QHBoxLayout()
        self.registry_layout = QtWidgets.QVBoxLayout()
        self.distribution_layout = QtWidgets.QVBoxLayout()
        self.contents_l.addLayout(self.registry_layout, stretch=self.registry_stretch)
        self.contents_l.addLayout(self.distribution_layout, stretch=1)
    
        self.main_layout.addLayout(self.title_l)
        self.main_layout.addLayout(self.contents_l)

        self.add_plant_page = AddPlantPage() 


        # self.main_layout.addWidget(button := QtWidgets.QPushButton("Paint"))

    def init_title(self):
        self.title_l.addWidget(title := QtWidgets.QLabel("Plant Registry"))
        title_font = title.font()
        # title_font.setBold(True)
        title_font.setPointSize(25)
        title.setFont(title_font)
        self.title_l.addStretch()

        self.clear_bttn_w = QtWidgets.QPushButton("clear")
        self.title_l.addWidget(self.clear_bttn_w)


    def init_registry(self):
        layout = self.registry_layout
        layout.setAlignment(QtCore.Qt.AlignTop)


        self.plant_thumbnail_w = QtWidgets.QLabel()
        self.plant_thumbnail_w.setProperty("dark_background", True)
        self.plant_thumbnail_w.setVisible(False)

        self.plant_thumbnail_w.setObjectName("PlantThumbnail")
        layout.addWidget(self.plant_thumbnail_w)
        self.plant_thumbnail_pixmap = QtGui.QPixmap()
        self.update_thumbnail_size()
        
        self.plant_list_w = QtWidgets.QListWidget()
        self.plant_list_w.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.plant_list_w.setAlternatingRowColors(True)
        self.plant_list_w.setProperty("dark_background", True)

        self.plants_list_container_l = QtWidgets.QVBoxLayout()
        self.plants_list_container_l.setContentsMargins(0,0,0,0)
        self.plants_list_container_w = QtWidgets.QWidget()
        self.plants_list_container_w.setProperty("dark_background", True)
        self.plants_list_container_w.setLayout(self.plants_list_container_l)

        self.help_label_w = QtWidgets.QLabel("Press the + to add new plants")
        self.help_label_w.setProperty("transparent_background", True)
        self.help_label_w.setContentsMargins(10,10,10,10)
        self.help_label_w.setAlignment(QtCore.Qt.AlignHCenter)
        self.plants_list_container_l.addWidget(self.help_label_w)

        self.plants_list_container_l.addWidget(self.plant_list_w)

        self.plant_list_button_container_w = QtWidgets.QWidget()
        self.plants_list_container_l.addWidget(self.plant_list_button_container_w)
        self.plant_list_button_container_l = QtWidgets.QHBoxLayout()
        self.plant_list_button_container_w.setLayout(self.plant_list_button_container_l)
        self.plant_list_button_container_l.setContentsMargins(3,3,3,3)

        self.add_plant_bttn = QtWidgets.QPushButton("+")
        self.remove_plant_bttn = QtWidgets.QPushButton("-")
        self.edit_plant_bttn = QtWidgets.QPushButton("edit")

        self.plant_list_button_container_l.addWidget(self.edit_plant_bttn)
        self.plant_list_button_container_l.addStretch()
        self.plant_list_button_container_l.addWidget(self.remove_plant_bttn)
        self.plant_list_button_container_l.addWidget(self.add_plant_bttn)

        layout.addWidget(self.plants_list_container_w)

    def on_resize(self, event=None):
        self.update_thumbnail_size()
        super().resizeEvent(event)

    def update_thumbnail_size(self):
        if self.plant_thumbnail_pixmap.isNull():
            self.plant_thumbnail_w.setVisible(False)
            return

        self.plant_thumbnail_w.setVisible(True)

        thumbnail_width = self.width()/2*self.registry_stretch

        # scale image to half of its container
        scaled_pixmap = self.plant_thumbnail_pixmap.scaledToWidth(
            thumbnail_width,
            QtCore.Qt.SmoothTransformation
        )
        self.plant_thumbnail_w.setFixedSize(scaled_pixmap.size())

        


        # round image
        scaled_pixmap = qt_utils.round_pixmap_corners(scaled_pixmap)

        # draw text
        if(self.thumbnail_text != ""):
            qt_utils.add_text(scaled_pixmap, self.thumbnail_text, 10, scaled_pixmap.height()-10)

        self.plant_thumbnail_w.setPixmap(scaled_pixmap)
    
    def init_distribution(self):
        icons_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static/icons")

        layout = self.distribution_layout
        settings_w = QtWidgets.QWidget()
        settings_w.setProperty("dark_background", True)
        settings_w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        settings_l = QtWidgets.QVBoxLayout()
        settings_w.setLayout(settings_l)

        self.parm_dialog = hou.qt.ParmDialog(None)
        self.parm_dialog.setProperty("transparent_background", True)
        settings_l.addWidget(self.parm_dialog)
        layout.addWidget(settings_w)

        self.bake_b = QtWidgets.QPushButton("bake")
        layout.addWidget(self.bake_b)

        mode_w = QtWidgets.QWidget()
        mode_w.setProperty("dark_background", True)
        mode_w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addWidget(mode_w)
        mode_l = QtWidgets.QHBoxLayout()
        mode_w.setLayout(mode_l)

        self.dist_button_grp = QtWidgets.QButtonGroup()
        self.dist_button_grp.setExclusive(True)
        self.dist_place_b = DistButton("Place", os.path.join(icons_path, "dist_point.svg"), "point")
        self.dist_region_b = DistButton("Region", os.path.join(icons_path, "dist_region.svg"), "draw")
        self.dist_edit_b = DistButton("Edit", os.path.join(icons_path, "dist_edit.svg"), "edit")
        self.dist_delete_b = DistButton("Delete", os.path.join(icons_path, "dist_erase.svg"), "delete")

        self.dist_button_grp.addButton(self.dist_place_b)
        self.dist_button_grp.addButton(self.dist_region_b)
        self.dist_button_grp.addButton(self.dist_edit_b)
        self.dist_button_grp.addButton(self.dist_delete_b)


        mode_l.addWidget(self.dist_place_b)
        mode_l.addWidget(self.dist_region_b)
        mode_l.addWidget(self.dist_edit_b)
        mode_l.addWidget(self.dist_delete_b)


