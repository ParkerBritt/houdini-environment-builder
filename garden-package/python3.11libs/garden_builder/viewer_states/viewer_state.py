import hou
import json
import viewerstate.utils as su
import importlib
# from sidefx_stroke import StrokeState

import garden_builder.viewer_states.state_mode
importlib.reload(garden_builder.viewer_states.state_mode)
from garden_builder.viewer_states.state_mode import ViewerMode

import garden_builder.viewer_states.sidefx_stroke
importlib.reload(garden_builder.viewer_states.sidefx_stroke)
from garden_builder.viewer_states.sidefx_stroke import StrokeState

# String constants
STROKEMERGE_NODE = 'stroke_merge'
STROKECACHE_PARM = 'strokegeo'
NUMSTROKES_PARM = 'stroke_numstrokes'
ENABLECACHE_TOGGLE = 'enable_caching'

_global_kwargs = {}

# set args as global var
# allows caller to inject kwargs for viewer state template to read in and pass to child functions
def set_global_kwargs(kwargs):
    global _global_kwargs
    _global_kwargs = kwargs


class DrawCurveState(StrokeState):
    def __init__(self, state_name, scene_viewer):
        self.node = None
        self.state_name = state_name
        self.scene_viewer = scene_viewer
        super().__init__()
        self.mode = None
        
        # handle
        self.xform_handle = hou.Handle(self.scene_viewer, "Xform")

        self.init_drawables()

        self.terrain_active_platform = None
        self.terrain_hover_platform = None

        self.water_hover_id = None
        self.water_hover_type = None

        # terrain adjust
        self.terrain_start_x = 0
        self.terrain_start_y = 0
        self.terrain_start_height = 0
        self.terrain_start_smoothness = 0
        self.terrain_json_parm = None
        

        # points bit
        self.pressed = False
        self.index = 0    
        self.is_left_down = False

    def init_drawables(self):
        # drawables
        self.plant_selection_drawable = None
        self.terrain_arrow_drawable = None
        self.terrain_hover_prim_drawable = None

        self.plant_selection_drawable = hou.SimpleDrawable(self.scene_viewer, hou.Geometry() , f"{self.state_name}_selection_drawable")
        self.plant_selection_drawable.enable(False)
        self.plant_selection_drawable.show(True)
        self.plant_selection_drawable.setDisplayMode(hou.drawableDisplayMode.CurrentViewportMode)
        self.plant_selection_drawable.setXray(True)

        self.terrain_arrow_drawable = hou.SimpleDrawable(self.scene_viewer, hou.Geometry()  , f"{self.state_name}_terrain_arrow_drawable")
        self.terrain_arrow_drawable.enable(False)
        self.terrain_arrow_drawable.show(True)
        self.terrain_arrow_drawable.setDisplayMode(hou.drawableDisplayMode.CurrentViewportMode)

        self.terrain_hover_prim_drawable = hou.SimpleDrawable(self.scene_viewer, hou.Geometry()  , f"{self.state_name}_terrain_hover_prim_drawable")
        self.terrain_hover_prim_drawable.enable(False)
        self.terrain_hover_prim_drawable.show(False)
        self.terrain_hover_prim_drawable.setDisplayMode(hou.drawableDisplayMode.CurrentViewportMode)
        self.terrain_hover_prim_drawable.setXray(True)

        self.water_hover_prim_drawable = hou.SimpleDrawable(self.scene_viewer, hou.Geometry()  , f"{self.state_name}_water_hover_prim_drawable")
        self.water_hover_prim_drawable.enable(False)
        self.water_hover_prim_drawable.show(False)
        self.water_hover_prim_drawable.setDisplayMode(hou.drawableDisplayMode.CurrentViewportMode)
        self.water_hover_prim_drawable.setXray(True)


    def read_mode(self):
        print("reading mode")
        mode_str = self.node.parm("state_mode").evalAsString()
        new_mode = ViewerMode.map_state(mode_str)
        mode_changed = new_mode != self.mode
        
        
        if(mode_changed):
            print("mode changed:", mode_str)
            self.set_mode(new_mode)
            self.xform_handle.show(False)

            # set drawable visiblity
            # plant selection visiblity
            if(self.plant_selection_drawable):
                is_plant_mode = self.mode in (ViewerMode.PLANT_DRAW, ViewerMode.PLANT_EDIT_SELECTION, ViewerMode.PLANT_EDIT_HANDLE, ViewerMode.PLANT_ERASE)
                self.plant_selection_drawable.enable(is_plant_mode)
                self.plant_selection_drawable.show(is_plant_mode)
                print("setting plant seleciton to:", is_plant_mode)

            # Terrain Arrow
            show_terrain_hover_drawable = self.mode in (ViewerMode.TERRAIN_SELECT, ViewerMode.TERRAIN_DELETE)
            has_active_platform = (self.terrain_active_platform is not None and self.terrain_active_platform != -1 )
            show_terrain_arrow_drawable = self.mode == ViewerMode.TERRAIN_SELECT and has_active_platform
            if(self.terrain_arrow_drawable):
                self.terrain_arrow_drawable.enable(show_terrain_arrow_drawable)
                self.terrain_arrow_drawable.show(show_terrain_arrow_drawable)
                print("arrow drawable visiblity:", show_terrain_arrow_drawable)

            # Terrain hover
            if(self.terrain_hover_prim_drawable):
                self.terrain_hover_prim_drawable.enable(show_terrain_hover_drawable)
                self.terrain_hover_prim_drawable.show(show_terrain_hover_drawable)
                print("setting hover prim to:", show_terrain_hover_drawable)

            if(self.water_hover_prim_drawable):
                show_water_hover_drawable = self.mode == ViewerMode.WATER_DELETE
                self.water_hover_prim_drawable.enable(show_water_hover_drawable)
                self.water_hover_prim_drawable.show(show_water_hover_drawable)
                print("water hover visibility:", show_water_hover_drawable)
            

    def onPostStroke(self, node, ui_event, captured_parms):
        
        if node.parm("cachestrokes").evalAsInt():
            cacheStrokes(node)
            
        if(self.mode == ViewerMode.PLANT_EDIT_SELECTION):
            self.set_mode(ViewerMode.PLANT_EDIT_HANDLE)
            self.xform_handle.show(True)
            center_node = self.node.node("draw_shape")
            if(center_node is None):
                print("self.node: ", self.node)
                raise Exception("no node 'draw_shape'")
            selection_center = center_node.geometry().boundingBox().center()
            self.node.setParms({"edit_mode_pivotx":selection_center.x(),"edit_mode_pivoty":selection_center.y(),"edit_mode_pivotz":selection_center.z(),
                                "edit_mode_translatex":0, "edit_mode_translatey":0, "edit_mode_translatez":0})




        # bake action after drawing delete area
        if(self.mode == ViewerMode.PLANT_ERASE):
            self.bake()
        
        
    def bake(self):
        print("baking for new curve")
        in_kwargs = {"node":self.node}
        self.node.hm().stash(in_kwargs)
        
        

    def pointCount(self):
        """ This is how you get the number of instances 
            in a multiparm. 
        """
        try:
            multiparm = self.node.parm("points")
            return multiparm.evalAsInt()
        except:
            return 0

    def start(self):
        if not self.pressed:
            self.scene_viewer.beginStateUndo("Add point")
            self.index = self.pointCount()
            multiparm = self.node.parm("points")
            multiparm.insertMultiParmInstance(self.index)

        self.pressed = True

    def finish(self):
        if self.pressed:
            self.scene_viewer.endStateUndo()
        self.pressed = False


    def onEnter(self, kwargs):
        self.node = kwargs["node"]
        if not self.node:
            raise

        super().onEnter(kwargs)
        self.xform_handle.show(False)

        # terrain
        self.terrain_platform_collision = self.node.node("draw_terrain/OUT_viewer_terrain_platforms_collision").geometry()
        self.terrain_active_platform_geo = self.node.node("draw_terrain/OUT_viewer_terrain_active_platform").geometry()
        self.terrain_json_parm = self.node.parm("terrain_json")

        # water
        self.water_platform_collision = self.node.node("water/OUT_water_viewstate_collision").geometry()

        # set geometry
        self.plant_selection_drawable.setGeometry(self.node.node("drawables/plant_selection").geometry())
        self.terrain_arrow_drawable.setGeometry(self.node.node("drawables/terrain_arrow_controller").geometry())
        self.terrain_hover_prim_drawable.setGeometry(self.node.node("drawables/terrain_active_prim").geometry())
        self.water_hover_prim_drawable.setGeometry(self.node.node("drawables/water_hover_prim").geometry())

        self.read_mode()



    def onInterrupt(self,kwargs):
        self.finish()

        self.plant_selection_drawable.show(False)
        self.terrain_arrow_drawable.show(False)
        self.terrain_hover_prim_drawable.show(False)

        self.read_mode()

    def onResume(self, kwargs):
        self.read_mode()

        self.plant_selection_drawable.show(True)
        self.terrain_arrow_drawable.show(True)
        self.terrain_hover_prim_drawable.show(True)


    def onKeyEvent(self, kwargs):
        ui_event = kwargs["ui_event"]
        key = ui_event.device().keyString().lower()
    
        if key == "p":
            self.set_mode(ViewerMode.PLANT_PLACE)
            self.scene_viewer.setPromptMessage("Switched to Place Points Mode.")
        elif key == "d":
            self.set_mode(ViewerMode.PLANT_DRAW)
            self.scene_viewer.setPromptMessage("Switched to Draw Mode.")

    def set_mode(self, in_mode):
        """Set the viewerstate mode to a ViewerMode value"""
        
        if(self.mode == in_mode):
            return

        self.mode = in_mode
        self.state_mode_parm = self.node.parm("state_mode") 

        # set mode parameter
        self.state_mode_parm.set(ViewerMode.map_state(self.mode))



            
    def onMouseEvent(self, kwargs):
        
        
        
        ui_event = kwargs["ui_event"]
        device = ui_event.device()
        reason = ui_event.reason()
        origin, direction = ui_event.ray()
        
        # remove handle when they start drawing a new curve
        if(device.isLeftButton()):
            self.xform_handle.show(False)
            # if new stroke
            if(not self.is_left_down and self.mode in (ViewerMode.PLANT_EDIT_HANDLE, ViewerMode.PLANT_DRAW, ViewerMode.PLANT_PLACE)):
                # bake changes
                self.bake()

                # reset transforms for handle
                if(self.mode == ViewerMode.PLANT_EDIT_HANDLE):
                    self.set_mode(ViewerMode.PLANT_EDIT_SELECTION)

                
                                
            self.is_left_down = True
        else:
            self.is_left_down = False
            
        
        if(self.mode in [ViewerMode.PLANT_DRAW, ViewerMode.PLANT_ERASE, ViewerMode.PLANT_EDIT_SELECTION]):
            kwargs["node"] = self.node.node("drawcurve1")
            kwargs["parm_node"] = self.node
            kwargs["param_prefix"] = "plants_"
            kwargs["stroke_num_parm_name"] = 'plants_stroke_numstrokes'
            super().onMouseEvent(kwargs)
        elif(self.mode == ViewerMode.TERRAIN_DRAW):

            if(reason==hou.uiEventReason.Start): # only run once per curve
                # add new item to json data
                json_data = json.loads(self.terrain_json_parm.evalAsString())
                new_prim_data = {"height":10, "smoothness":0.1}
                json_data.append(new_prim_data)
                self.terrain_json_parm.set(json.dumps(json_data))

            # setup and run inhereted state
            kwargs["node"] = self.node.node("terrain_curve")
            kwargs["parm_node"] = self.node
            kwargs["param_prefix"] = "terrain_"
            kwargs["stroke_num_parm_name"] = 'terrain_stroke_numstrokes'
            super().onMouseEvent(kwargs)
        elif(self.mode == ViewerMode.WATER_CURVE):
            # setup and run inhereted state
            kwargs["node"] = self.node.node("water/water_draw_river")
            kwargs["parm_node"] = self.node
            kwargs["param_prefix"] = "river_"
            kwargs["stroke_num_parm_name"] = 'river_stroke_numstrokes'
            super().onMouseEvent(kwargs)
        elif(self.mode == ViewerMode.WATER_REGION):
            # setup and run inhereted state
            kwargs["node"] = self.node.node("water/water_draw_lake")
            kwargs["parm_node"] = self.node
            kwargs["param_prefix"] = "lake_"
            kwargs["stroke_num_parm_name"] = 'lake_stroke_numstrokes'
            super().onMouseEvent(kwargs)

        elif(self.mode==ViewerMode.PLANT_PLACE):
            origin, direction = ui_event.ray()
            
            geometry = self.node.node("OUT_terrain_state_intersect").geometry()
            prim_num, position, normal, uvw = su.sopGeometryIntersection(geometry, origin, direction)
               
            # Create/move point if LMB is down
            if device.isLeftButton():
                self.start()
                # set the point position
                self.node.parm("usept%d" % self.index).set(1)
                self.node.parmTuple("pt%d" % self.index).set(position)
                
            else:
                self.finish()
                
            return True
        elif(self.mode == ViewerMode.TERRAIN_SELECT):
            prim_num = None
            # click prim
            if ((reason==hou.uiEventReason.Picked) and self.terrain_hover_platform is not None and self.terrain_hover_platform != -1 ):
                
                self.terrain_active_platform = self.terrain_hover_platform

                self.node.setParms({"active_terrain_platform":self.terrain_active_platform})

                self.terrain_arrow_drawable.enable(True)
                self.terrain_arrow_drawable.show(True)

                # set arrow start position
                geo_center = self.terrain_platform_collision.prim(self.terrain_active_platform).boundingBox().center()
                handle_data = json.loads(self.terrain_json_parm.evalAsString())
                height = handle_data[self.terrain_active_platform]["height"]
                geo_center[1] += height
                arrow_xform = hou.hmath.buildTranslate(geo_center)
                self.terrain_arrow_drawable.setTransform(arrow_xform)

                # reset hover platform
                self.terrain_hover_platform = -1
                self.node.setParms({"hover_terrain_platform":-1})
            # hover over prim
            elif(reason==hou.uiEventReason.Located):
                prim_num, position, normal, uvw = su.sopGeometryIntersection(self.terrain_platform_collision, origin, direction)
                if(prim_num!=self.terrain_hover_platform and prim_num != self.terrain_active_platform):
                    print("new hover prim", prim_num)
                    self.terrain_hover_platform = prim_num
                    self.node.setParms({"hover_terrain_platform":prim_num})
            # adjust prim
            elif(self.terrain_active_platform is not None and self.terrain_active_platform != -1 ):
                json_str = self.terrain_json_parm.evalAsString()
                handle_data = json.loads(json_str)

                prim_data = handle_data[self.terrain_active_platform]
                if(reason==hou.uiEventReason.Start):
                    self.terrain_start_y = device.mouseY()
                    self.terrain_start_x = device.mouseX()
                    
                    height = prim_data["height"]
                    smoothness = prim_data["smoothness"]
                    self.terrain_start_height = height
                    self.terrain_start_smoothness = smoothness

                elif(reason==hou.uiEventReason.Active):
                    geo_center = self.terrain_platform_collision.prim(self.terrain_active_platform).boundingBox().center()
                    y_offset = device.mouseY()-self.terrain_start_y
                    x_offset = device.mouseX()-self.terrain_start_x
                    
                    print("start_height:", self.terrain_start_height)

                    # decide which value to modify
                    smoothness = self.terrain_start_smoothness + x_offset/150
                    prim_data["smoothness"] = smoothness

                    height = self.terrain_start_height + y_offset/10
                    prim_data["height"] = height

                    geo_center[1]+=height
                    
                    arrow_pos = hou.hmath.buildTranslate(geo_center)            
                    self.terrain_arrow_drawable.setTransform(arrow_pos)
                    
                    self.terrain_json_parm.set(json.dumps(handle_data))
                    self.node.setParms({"terrain_active_smooth":smoothness, "terrain_active_height": height})
        elif(self.mode == ViewerMode.TERRAIN_DELETE):
            if(reason==hou.uiEventReason.Located):
                prim_num, position, normal, uvw = su.sopGeometryIntersection(self.terrain_platform_collision, origin, direction)
                self.terrain_hover_platform = prim_num
                self.node.setParms({"hover_terrain_platform":prim_num})
            elif ((reason==hou.uiEventReason.Picked) and self.terrain_hover_platform is not None and self.terrain_hover_platform != -1 ):
                
                self.node.parm("terrain_stroke_numstrokes").removeMultiParmInstance(self.terrain_hover_platform)

                json_str = self.terrain_json_parm.evalAsString()
                terrain_data = json.loads(json_str)
                terrain_data.pop(self.terrain_hover_platform)

                self.terrain_json_parm.set(json.dumps(terrain_data))

                # reset hover platform
                self.terrain_hover_platform = -1
                self.terrain_active_platform = -1
                self.node.setParms({"hover_terrain_platform":-1, "active_terrain_platform":-1})
        elif(self.mode == ViewerMode.WATER_DELETE):
            if(reason==hou.uiEventReason.Located):
                prim_num, position, normal, uvw = su.sopGeometryIntersection(self.water_platform_collision, origin, direction)
                if(prim_num!=-1):
                    print("prim_num:", prim_num)
                    self.water_hover_id = self.water_platform_collision.prim(prim_num).intAttribValue("prim_id")
                    self.water_hover_type = self.water_platform_collision.prim(prim_num).stringAttribValue("water_type")
                    self.node.setParms({"water_hover_id":self.water_hover_id, "water_hover_type":self.water_hover_type})
                    self.node.parm("water_hover_id").pressButton()
            elif ((reason==hou.uiEventReason.Picked) and self.water_hover_id is not None and self.water_hover_id != -1 ):
                stroke_parm = self.node.parm(self.water_hover_type+"_stroke_numstrokes")
                stroke_parm.removeMultiParmInstance(self.water_hover_id)

                
                # reset hover platform
                self.water_hover_id = -1
                self.node.setParms({"water_hover_id":-1})
                self.node.parm("water_hover_id").pressButton()
                    
                    


            
            
def cacheStrokes(node):
    stroke_node = node.node(STROKEMERGE_NODE)
    if not stroke_node:
        return

    stroke_geo = stroke_node.geometry()
    if not stroke_geo:
        return 

    node.parm(STROKECACHE_PARM).set(stroke_geo)
    node.parm(NUMSTROKES_PARM).revertToDefaults()



def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """
    global _global_kwargs
    kwargs = _global_kwargs
    state_typename = kwargs['type'].definition().sections()['DefaultState'].contents()
    state_label = 'DrawCurve'
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(DrawCurveState)
    template.bindIcon(kwargs['type'].icon())

    # Hotkeys
    hotkey_definitions = hou.PluginHotkeyDefinitions()
    realtime = su.defineHotkey(hotkey_definitions, state_typename, 'realtime_mode', '0', 'realtime', 'Enable realtime mode')
    su.defineHotkey(hotkey_definitions, state_typename, "placement_mode", "P", "placement", "Switch to Placement Mode")
    su.defineHotkey(hotkey_definitions, state_typename, "draw_mode", "D", "drawcurve", "Switch to Draw Mode")
    template.bindHotkeyDefinitions(hotkey_definitions)
    
    # bind a static handle to node parameters. 
    template.bindHandleStatic( "xform", "Xform", 
        [
            ("edit_mode_translatex", "tx"),
            ("edit_mode_translatey", "ty"),
            ("edit_mode_translatez", "tz"),
            ("edit_mode_pivotx", "px"),
            ("edit_mode_pivoty", "py"),
            ("edit_mode_pivotz", "pz"),
            ("edit_mode_rotatex", "rx"),
            ("edit_mode_rotatey", "ry"),
            ("edit_mode_rotatez", "rz"),
        ])
    
    # Define the popup menu
    m = hou.ViewerStateMenu('stroke_menu', 'Stroke')
    
    m.addToggleItem('realtime_mode', 'Draw realtime', True, hotkey=realtime)

    # Bind the popup menu to the stroke state
    template.bindMenu(m)

    return template

