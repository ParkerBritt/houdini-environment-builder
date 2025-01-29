from PySide2 import QtWidgets, QtGui, QtCore
from importlib import reload
import os, hou, logging

logger = logging.getLogger("add_plant_controller")
logger.setLevel(logging.DEBUG)

import garden_builder.utils.qt_style
reload(garden_builder.utils.qt_style)
from garden_builder.utils.qt_style import set_valid

import garden_builder.viewer_states.state_mode
reload(garden_builder.viewer_states.state_mode)
from garden_builder.viewer_states.state_mode import ViewerMode

class AddPlantController():
    """Controller for the 'add_plant_page' widget"""

    def __init__(self, main_controller, page_container):
        self.node = None
        self.main_controller = main_controller
        self.plant_controller = self.main_controller.plant_controller
        self.page_container = page_container
        self.plants_page = self.page_container.plants_page
        self.add_plant_page = self.page_container.add_plant_page

    def connect_signals(self):
        """Connect qt signals to appropriate slots."""
        self.add_plant_page.settings_form_l.method_w.currentTextChanged.connect(self.on_geo_method_changed)
        self.add_plant_page.settings_form_l.template_w.currentTextChanged.connect(self.set_procedural_interface)
        self.add_plant_page.pageOpened.connect(self.on_add_plant_page_opened)
        self.add_plant_page.done_bttn_w.clicked.connect(self.on_add_plant_done)
        self.plants_page.remove_plant_bttn.clicked.connect(self.on_plant_remove_clicked)

    def on_plant_remove_clicked(self):
        """Remove a plant from the plant registry."""
        # TODO: maybe add confirmation box, might not be necessary since you can undo
        if(not self.node):
            logger.warning("Attempted to remove plant but no node was selected.")
            return
        
        # remove plant from registry parameter
        plant_list = self.plants_page.plant_list_w 
        multiparm_index = plant_list.currentRow()+1
        last_id = self.node.parm(f"pr_id{multiparm_index}").evalAsInt()

        method = self.node.parm(f"pr_method{multiparm_index}").evalAsString()
        logger.debug(f"type: {method}")
        if("procedural" == method):
            # get method name
            template_name = self.node.parm(f"pr_procedural_template{multiparm_index}").evalAsString()

            registry_node = self.node.node(f"plants/{template_name}_registry")
            registry_parm = registry_node.parm("registry")
            logger.debug(f"REGISTRY NODE: {registry_node}")
            if(not registry_node):
                logger.error(f"registry node doesn't exist for: {template_name}")
                return

            regsitry_cnt = registry_parm.evalAsInt()
            for i in range(regsitry_cnt):
                procedural_multiparm_index = i+1
                id_parm = registry_node.parm(f"id{procedural_multiparm_index}")
                if(not id_parm):
                    logger.error(f"can't find parm: id{procedural_multiparm_index}")
                    return
                id = id_parm.evalAsInt()
                if(id==last_id):
                    registry_parm.removeMultiParmInstance(procedural_multiparm_index-1)
                    break

        # delete points with the removed plant id
        self.node.parm("delete_plant_id").set(last_id)
        self.node.parm("delete_registry_plant").pressButton()
        logger.debug(f"removing plant registry multiparm index: {multiparm_index-1}")
        self.node.parm("plant_registry").removeMultiParmInstance(multiparm_index-1)

        # update plant list
        self.plant_controller.populate_plant_list(refresh_registry=True)

    def on_add_plant_page_opened(self):
        """Reset qt parameters when page opened."""
        self.add_plant_page.settings_form_l.clear()
        set_valid(self.add_plant_page.settings_form_l.name_w, True)
        set_valid(self.add_plant_page.settings_form_l.proxy_file_w.line_w, True)
        set_valid(self.add_plant_page.settings_form_l.render_file_w.line_w, True)
        set_valid(self.add_plant_page.settings_form_l.proxy_node_w.line_w, True)
        set_valid(self.add_plant_page.settings_form_l.render_node_w.line_w, True)

        # reset state
        self.node.parm("state_mode").set(ViewerMode.map_state(ViewerMode.INACTIVE))



    def onNodePathChanged(self, node):
        """Refetch plant registry when node path changes."""
        self.node = node

    def on_geo_method_changed(self, text):
        """Hide and show parameters when geometry method parameter is changed."""

        print("item changed:", text)
        # show the appropriate parameters for each geometry method
        settings_l = self.add_plant_page.settings_form_l
        manual_proxy = not settings_l.auto_proxy_w.isChecked()
        settings_l.proxy_file_row_w.setVisible(text=="File" and manual_proxy)
        settings_l.render_file_row_w.setVisible(text=="File")
        settings_l.proxy_node_row_w.setVisible(text=="Sop" and manual_proxy)
        settings_l.render_node_row_w.setVisible(text=="Sop")
        settings_l.template_row_w.setVisible(text=="Procedural")
        settings_l.auto_proxy_row_w.setVisible(text in ("File", "Sop"))

        if(text in ("File", "Sop")):
            self.add_plant_page.parm_dialog.setNode(None)
        elif(text == "Procedural"):
            self.set_procedural_interface()
    
    def convert_procedural_template_name(self, in_name):
        return in_name.lower().replace(" ", "_")
        

    def set_procedural_interface(self):
        """Set controls panel to appropriate node."""
        settings_l = self.add_plant_page.settings_form_l
        template_name = self.convert_procedural_template_name(settings_l.template_w.currentText())
        

        interface_node = self.node.node(f"plants/{template_name}_interface")
        if(not interface_node):
            print("ERROR: node doesn't exist for:", template_name)

        self.reset_procedural_interface(interface_node)
        self.add_plant_page.parm_dialog.setNode(interface_node)

    def reset_procedural_interface(self, node):
        """reset procedural inteface parameters to default values."""
        for parm in node.parms():
            parm.revertToDefaults()

    def validate_settings(self):
        """Check the user settings are set to expected values"""
        settings_l = self.add_plant_page.settings_form_l
        plant_name = settings_l.name_w.text().strip().title()
        valid_settings = True 

        if(plant_name==""):
            set_valid(settings_l.name_w, False)
            valid_settings = False
        else:
            set_valid(settings_l.name_w, True)

        
        valid_geo_exts = [".obj", ".fbx", ".abc", ".geo", ".bgeo"]
        method_txt = settings_l.method_w.currentText()
        auto_proxy = self.add_plant_page.settings_form_l.auto_proxy_w.isChecked()

        if(method_txt == "File"):
            # check files are valid
            if(not auto_proxy): # skip validating proxy if auto proxy
                proxy_file_path = os.path.expandvars(settings_l.proxy_file_w.text())
                # file exists and has the right extension
                if(not os.path.exists(proxy_file_path) or
                   not os.path.splitext(proxy_file_path)[1] in valid_geo_exts):
                    set_valid(settings_l.proxy_file_w.line_w, False)
                    valid_settings = False
                else:
                    set_valid(settings_l.proxy_file_w.line_w, True)

            render_file_path = os.path.expandvars(settings_l.render_file_w.text())
            if(not os.path.exists(render_file_path) or
               not os.path.splitext(render_file_path)[1] in valid_geo_exts):
                set_valid(settings_l.render_file_w.line_w, False)
                valid_settings = False
            else:
                set_valid(settings_l.render_file_w.line_w, True)

        elif(method_txt == "Sop"):
            # check nodes are valid
            if(not auto_proxy): # skip validating proxy if auto proxy
                proxy_node_path = os.path.expandvars(settings_l.proxy_node_w.text())
                proxy_node = hou.node(proxy_node_path)
                if(not proxy_node or
                   not isinstance(proxy_node, hou.SopNode)):
                    set_valid(settings_l.proxy_node_w.line_w, False)
                    valid_settings = False
                else:
                    set_valid(settings_l.proxy_node_w.line_w, True)

            render_node_path = os.path.expandvars(settings_l.render_node_w.text())
            render_node = hou.node(render_node_path)
            if(not render_node or
               not isinstance(render_node, hou.SopNode)):
                set_valid(settings_l.render_node_w.line_w, False)
                valid_settings = False
            else:
                set_valid(settings_l.render_node_w.line_w, True)

        return valid_settings
                

    def on_add_plant_done(self):
        """Execute setup when user finishes adding a new plant.

        Validates input values then decide if user can continue.
        Set hda parameters based on qt inputs.
        """
        settings_l = self.add_plant_page.settings_form_l

        plant_registry_parm = self.node.parm("plant_registry")
        multiparm_index = plant_registry_parm.evalAsInt()+1

        plant_name = settings_l.name_w.text().strip().title()
        method_txt = settings_l.method_w.currentText()
        auto_proxy = self.add_plant_page.settings_form_l.auto_proxy_w.isChecked()



        # validate inputs
        valid_settings = self.validate_settings()
        if( not valid_settings):
            return

        # add new multiparm instance
        plant_registry_parm.set(multiparm_index)

        last_plant_id = self.node.parm("last_added_plant_id").evalAsInt()
        self.node.parm("last_added_plant_id").set(last_plant_id+1)
        # TODO: split up setting parameters to separate function
        self.node.setParms({
            f"pr_name{multiparm_index}" : plant_name,
            f"pr_method{multiparm_index}" : settings_l.method_w.currentIndex(),
            f"pr_auto_proxy{multiparm_index}" : settings_l.auto_proxy_w.isChecked(),
            f"pr_id{multiparm_index}" : last_plant_id
        })

        if(method_txt == "File"):
            self.node.parm(f"pr_geo_render_file{multiparm_index}").set(settings_l.render_file_w.text())
            if(not auto_proxy):
                self.node.parm(f"pr_geo_proxy_file{multiparm_index}").set(settings_l.proxy_file_w.text())
        elif(method_txt == "Sop"):
            self.node.parm(f"pr_geo_render_sop{multiparm_index}").set(settings_l.render_node_w.text())
            if(not auto_proxy):
                self.node.parm(f"pr_geo_proxy_sop{multiparm_index}").set(settings_l.proxy_node_w.text())
        elif(method_txt == "Procedural"):
            self.create_procedural_instance(last_plant_id)



        self.plant_controller.populate_plant_registry()
        self.plant_controller.populate_plant_list()
        self.main_controller.set_page(self.page_container.plants_page)

    def create_procedural_instance(self, id):
        """Create a plant instance in the registry of a procedural plant
        
        Args:
            id (int): id of the instance to be created.
        """
        settings_l = self.add_plant_page.settings_form_l
        template_name = self.convert_procedural_template_name(settings_l.template_w.currentText())
        template_node_name = template_name.lower()
        

        # getting mapping and registry nodes
        mapping_node = self.node.node(f"plants/{template_node_name.lower()}_mapping")
        if(not mapping_node):
            print("ERROR: mapping node doesn't exist for:", template_name)
            return
        registry_node = self.node.node(f"plants/{template_node_name.lower()}_registry")
        if(not registry_node):
            print("ERROR: registry node doesn't exist for:", template_name)
            return

        # add new registry instance
        registry_parm = registry_node.parm("registry")
        registry_parm.set(registry_parm.evalAsInt()+1)
        multiparm_index=registry_parm.evalAsInt()

        # set instance id
        registry_node.parm(f"id{multiparm_index}").set(id)

        # set registry instance to mapping parameters
        for mapping_parm in mapping_node.parms():
            registry_parm = registry_node.parm(mapping_parm.name()+str(multiparm_index))
            if(registry_parm):
                print("parm exists:", registry_parm.name())
                registry_parm.set(mapping_parm.eval())
            else:
                print("parm doesn't exist:", mapping_parm.name())
