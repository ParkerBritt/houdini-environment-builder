from PySide2 import QtWidgets, QtGui, QtCore
import hou
from importlib import reload

import garden_builder.widgets.landing_page
reload(garden_builder.widgets.landing_page)
from garden_builder.widgets.landing_page import LandingPage

import garden_builder.widgets.terrain_page
reload(garden_builder.widgets.terrain_page)
from garden_builder.widgets.terrain_page import TerrainPage

import garden_builder.widgets.plants_page
reload(garden_builder.widgets.plants_page)
from garden_builder.widgets.plants_page import PlantsPage

import garden_builder.widgets.stage_page
reload(garden_builder.widgets.stage_page)
from garden_builder.widgets.stage_page import StagePage

import garden_builder.widgets.render_page
reload(garden_builder.widgets.render_page)
from garden_builder.widgets.render_page import RenderPage

import garden_builder.utils.qt_style
reload(garden_builder.utils.qt_style)
from garden_builder.utils.qt_style import QT_Style


import garden_builder.widgets.add_plant_page
reload(garden_builder.widgets.add_plant_page)
from garden_builder.widgets.add_plant_page import AddPlantPage


class MainUIFrame(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        background_widget = QtWidgets.QWidget()
        background_widget.setObjectName("PageContainer")
        background_widget.setStyleSheet(QT_Style.get_style_sheet())
        self.background_layout = QtWidgets.QVBoxLayout()
        self.background_layout.addWidget(background_widget)
        self.setLayout(self.background_layout)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        background_widget.setLayout(self.main_layout)
        background_widget.setProperty("light_background", True)

        self.button_container_widget = QtWidgets.QWidget()
        self.button_container_widget.setMaximumWidth(200)
        self.button_container_widget.setMinimumWidth(0)

        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.setAlignment(QtCore.Qt.AlignTop)
        self.button_layout.setSpacing(15)

        self.button_container_widget.setLayout(self.button_layout)
        self.main_layout.addWidget(self.button_container_widget)

        self.button_group = QtWidgets.QButtonGroup()
        self.button_terrain = self._new_side_button("Terrain", self.button_group, self.button_layout)
        self.button_plants = self._new_side_button("Plants", self.button_group, self.button_layout)
        # self.button_path = self._new_side_button("Path", self.button_group, self.button_layout)
        self.button_stage = self._new_side_button("Stage", self.button_group, self.button_layout)
        self.button_render = self._new_side_button("Render", self.button_group, self.button_layout)

        page_container = QtWidgets.QWidget() 
        self.main_layout.addWidget(page_container)
        # page_container.setObjectName("Page")
        # page_container.setStyleSheet("#Page {background-color: red ; border-radius: 20px}")
        # self.page_container_layout = QtWidgets.QVBoxLayout()
        self.page_container_layout = QtWidgets.QStackedLayout()
        page_container.setLayout(self.page_container_layout)

        self.landing_page = LandingPage()
        self.terrain_page = TerrainPage()
        self.plants_page = PlantsPage()
        self.stage_page = StagePage()
        self.render_page = RenderPage()

        self.page_container_layout.addWidget(self.landing_page)
        self.page_container_layout.addWidget(self.terrain_page)
        self.page_container_layout.addWidget(self.plants_page)
        self.page_container_layout.addWidget(self.stage_page)
        self.page_container_layout.addWidget(self.render_page)

        # extra pages
        self.add_plant_page = AddPlantPage()
        self.page_container_layout.addWidget(self.add_plant_page)

    def set_page(self, page):
        self.page_container_layout.setCurrentWidget(page)



    def _new_side_button(self, button_name, button_group, button_layout):
        button = QtWidgets.QPushButton(button_name)

        button_font = button.font()
        button_font.setPointSize(18)
        button.setFont(button_font)

        button.setCheckable(True)
        button_group.addButton(button)
        button_layout.addWidget(button)
        return button







