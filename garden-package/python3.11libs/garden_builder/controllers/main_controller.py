from importlib import reload


import garden_builder.controllers.plant_controller
reload(garden_builder.controllers.plant_controller)
from garden_builder.controllers.plant_controller import PlantController

import garden_builder.controllers.add_plant_controller
reload(garden_builder.controllers.add_plant_controller)
from garden_builder.controllers.add_plant_controller import AddPlantController

import garden_builder.controllers.terrain_controller
reload(garden_builder.controllers.terrain_controller)
from garden_builder.controllers.terrain_controller import TerrainController

import garden_builder.controllers.stage_controller
reload(garden_builder.controllers.stage_controller)
from garden_builder.controllers.stage_controller import StageController

import garden_builder.controllers.render_controller
reload(garden_builder.controllers.render_controller)
from garden_builder.controllers.render_controller import RenderController

class Controller():
    """Control the functionality of the interface as well as child controllers"""
    def __init__(self, node, page_container, navigation_bar):
        self.node = node
        self.page_container = page_container
        self.current_page = None
        self.navigation_bar = navigation_bar


        self.plant_controller = PlantController(self, self.page_container)
        self.add_plant_controller = AddPlantController(self, self.page_container)
        self.terrain_controller = TerrainController(self, self.page_container)
        self.stage_controller = StageController(self, self.page_container)
        self.render_controller = RenderController(self, self.page_container)

        self.child_controllers = [
            self.plant_controller,
            self.add_plant_controller,
            self.terrain_controller,
            self.stage_controller,
            self.render_controller,
        ]

        self.connect_signals()
        self.connect_container_buttons()

    def set_page(self, new_page):
        previous_page = self.current_page 
        if(previous_page):
            previous_page.pageClosed.emit()
        new_page.pageOpened.emit()

        self.navigation_bar.clear_pages()
        self.navigation_bar.add_page(new_page.name)
        self.page_container.set_page(new_page)
        self.current_page = new_page

    def onNodePathChanged(self, node):
        name_components = node.type().nameComponents()
        if(not (name_components[1] == "parker" and name_components[2] == "garden_builder")):
            print("invalid node type")
            return


        # set default page
        self.page_container.button_terrain.click()

        self.node = node

        for child_controller in self.child_controllers:
            if(hasattr(child_controller, "onNodePathChanged")):
                child_controller.onNodePathChanged(node)

        self.default_buttons()

    def connect_signals(self):
        for child_controller in self.child_controllers:
            if(hasattr(child_controller, "connect_signals")):
                child_controller.connect_signals()

    def default_buttons(self):
        for child_controller in self.child_controllers:
            if(hasattr(child_controller, "default_buttons")):
                child_controller.default_buttons()

    def connect_container_buttons(self):
        self.page_container.button_terrain.clicked.connect(lambda: self.set_page(self.page_container.terrain_page))
        self.page_container.button_plants.clicked.connect(lambda: self.set_page(self.page_container.plants_page))
        self.page_container.button_stage.clicked.connect(lambda: self.set_page(self.page_container.stage_page))
        self.page_container.button_render.clicked.connect(lambda: self.set_page(self.page_container.render_page))


