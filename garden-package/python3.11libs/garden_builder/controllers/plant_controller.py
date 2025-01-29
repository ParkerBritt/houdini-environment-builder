from PySide2 import QtWidgets, QtGui, QtCore
from importlib import reload
import os, hou

import garden_builder.model.plant_registry
reload(garden_builder.model.plant_registry)
from garden_builder.model.plant_registry import PlantRegistry

import garden_builder.model.plant
reload(garden_builder.model.plant)
from garden_builder.model.plant import Plant

import garden_builder.utils.qt_style
reload(garden_builder.utils.qt_style)
from garden_builder.utils.qt_style import set_valid

import garden_builder.viewer_states.state_mode
reload(garden_builder.viewer_states.state_mode)
from garden_builder.viewer_states.state_mode import ViewerMode


class PlantController():
    """Control the functionality of the plant page"""
    def __init__(self, main_controller, page_container):
        self.node = None
        self.main_controller = main_controller
        self.page_container = page_container
        self.plants_page = self.page_container.plants_page
        self.add_plant_page = self.page_container.add_plant_page

        # plant registry
        self.plant_registry = PlantRegistry(self.plants_page.plant_list_w)

    def connect_signals(self):
        """Connect qt signals to appropriate slots."""
        self.plants_page.dist_button_grp.buttonClicked.connect(self.on_dist_mode_clicked)
        self.plants_page.bake_b.clicked.connect(lambda: self.node.parm("decorator_bake").pressButton())
        self.plants_page.plant_list_w.itemClicked.connect(self.on_plant_list_clicked)
        self.plants_page.clear_bttn_w.clicked.connect(self.on_clear_bttn_clicked)

        # list buttons
        self.plants_page.add_plant_bttn.clicked.connect(self.on_plant_add_clicked)
        self.plants_page.edit_plant_bttn.clicked.connect(lambda: hou.ui.displayMessage("Editing not yet implemented"))
        self.add_plant_page.settings_form_l.auto_proxy_w.stateChanged.connect(self.on_auto_proxy_changed)


        # ADD PLANT PAGE
        # open add plant page
        self.add_plant_page.cancel_bttn_w.clicked.connect(lambda: self.main_controller.set_page(self.page_container.plants_page))

        self.plants_page.pageOpened.connect(self.on_page_opened)
        self.plants_page.pageClosed.connect(self.on_page_closed)

    def on_page_opened(self):
        self.node.setOutputForViewFlag(1)

        # reset state
        self.node.parm("state_mode").set(ViewerMode.map_state(ViewerMode.INACTIVE))

        # uncheck button
        checked_button = self.plants_page.dist_button_grp.checkedButton()
        if(checked_button is not None):
            self.plants_page.dist_button_grp.setExclusive(False)
            checked_button.setChecked(False)
            self.plants_page.dist_button_grp.setExclusive(True)
        # hide bake button
        self.plants_page.bake_b.setVisible(False)

        # check help message
        help_visibility = self.plants_page.plant_list_w.count()==0
        self.plants_page.help_label_w.setVisible(help_visibility)


    def on_page_closed(self):
        current_mode = ViewerMode.map_state(self.node.parm("state_mode").evalAsString())
        if(current_mode in (ViewerMode.PLANT_PLACE, ViewerMode.PLANT_DRAW)):
            print("baking changes on page closed")
            self.node.parm("decorator_bake").pressButton()

    def on_clear_bttn_clicked(self):
        if hou.ui.displayConfirmation("Clear all distributed plants?"):
            self.node.parm("clear_plants").pressButton()








    def on_auto_proxy_changed(self):
        """Hide and show parameters when auto proxy parameter is changed."""
        manual_proxy = not self.add_plant_page.settings_form_l.auto_proxy_w.isChecked()
        settings_l = self.add_plant_page.settings_form_l
        geo_method = self.add_plant_page.settings_form_l.method_w.currentText()
        settings_l.proxy_file_row_w.setVisible(manual_proxy and geo_method=="File")
        settings_l.proxy_node_row_w.setVisible(manual_proxy and geo_method=="Sop")
    
        

    def on_plant_add_clicked(self):
        """Dive into add plant page"""
        self.main_controller.set_page(self.page_container.add_plant_page)

    def onNodePathChanged(self, node):
        """Refetch plant registry when node path changes."""
        self.node = node

        self.populate_plant_list(refresh_registry=True)

    def populate_plant_registry(self):
        """Read plant registry on HDA and synchronize the python model."""
        self.plant_registry.clear()
        plant_cnt = self.node.parm("plant_registry").evalAsInt()
        for i, plant_num in enumerate(range(plant_cnt)):
            name_parm = self.node.parm(f"pr_name{plant_num+1}")
            if(not name_parm):
                print(f"missing parm: pr_name{plant_num+1}")
                continue

            name = name_parm.evalAsString()
            id = i
            new_plant = Plant(name, id)
            self.plant_registry.add_plant(new_plant)

    def populate_plant_list(self, refresh_registry=False):
        """Populate qt list with plant registry model data."""
        if(refresh_registry):
            self.populate_plant_registry()

        plant_list_w = self.plants_page.plant_list_w
        plant_list_w.clear()
        for plant in self.plant_registry.get_plants():
            plant_list_w.addItem(plant.name)

    def on_dist_mode_clicked(self, button):
        """Change plant distribution mode."""

        parm = self.node.parm("place_mode")
        parm.set(button.token)
        parm.pressButton()

        # bake button only visible for point and draw 
        self.plants_page.bake_b.setVisible(button.token in ("point", "draw"))

        # path to interface node to display
        interface_mapping = {
            "point":"distribution_operations/place_point_operation/interface",
            "draw":"distribution_operations/draw_region_operation/interface",
            "edit":"distribution_operations/edit_operation/interface",
            "delete":"distribution_operations/delete_interface"
        }
        print("switching to:", interface_mapping[button.token])
        self.plants_page.parm_dialog.setNode(self.node.node(interface_mapping[button.token]))

    def on_plant_list_clicked(self, item):
        """Update values when a new plant item is clicked
        
        Change thumbnail/text.
        Set instance ids.
        """
        # setup
        plant_list = self.plants_page.plant_list_w 
        selected_items = plant_list.selectedItems()
        last_item = selected_items[-1]
        selected_ids_str = ""

        # set thumbnail text
        self.plants_page.thumbnail_text = last_item.text()
        self.plants_page.update_thumbnail_size()

        # collect ids
        # TODO: fix id order
        for item in selected_items:
            multiparm_index = plant_list.row(item)+1
            print("multiparm index:", multiparm_index)
            id = self.node.parm(f"pr_id{multiparm_index}").evalAsInt()
            selected_ids_str += f"{id} "

        # set ids on node parm
        self.node.parm("sel_inst_ids").set(selected_ids_str)

        last_id = self.node.parm(f"pr_id{plant_list.currentRow()+1}").evalAsInt()
        print("LAST ID:", last_id)

        tmp_dir = self.node.parm("tmp_dir").evalAsString()
        if(not os.path.exists(tmp_dir)):
            print(f"temp dir doesn't exist '{tmp_dir}', creating new temp dir")
            self.node.hm().create_temp_dir({"node":self.node})
        tmp_dir = self.node.parm("tmp_dir").evalAsString()

        thumbnail_path = f"{tmp_dir}/plant_thumbnail_{last_id}.png"
        if(not os.path.exists(thumbnail_path)):
            print("image doesn't exist:", thumbnail_path)
            self.node.parm("thumbnail_id").set(last_id)
            self.node.parm("render_thumbnail").pressButton()
        if(os.path.exists(thumbnail_path)):
            self.plants_page.plant_thumbnail_pixmap = QtGui.QPixmap(thumbnail_path)
            self.plants_page.update_thumbnail_size()
        else:
            # set blank thumbnail
            self.plants_page.plant_thumbnail_pixmap = QtGui.QPixmap()
            self.plants_page.update_thumbnail_size()
            print("ERROR: attempt to create thumbnail failed")

    def default_buttons(self):
        """Set buttons to default states."""
        # set default distribution mode
        default_button = self.plants_page.dist_place_b
        default_button.click()

        # default add plant method
        self.add_plant_page.settings_form_l.method_w.setCurrentText("File")
        self.add_plant_page.settings_form_l.method_w.currentTextChanged.emit("File")


