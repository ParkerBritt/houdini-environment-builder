import json, tempfile, os

def stash(kwargs):
    knode = kwargs["node"]
    knode.parm("stash_plant_points").pressButton()
    
    reset_dist_parms(kwargs)

def delete_plant_type(kwargs):
    knode = kwargs["node"]
    knode.parm("delete_plant_state").set(True)
    knode.parm("stash_plant_points").pressButton()
    knode.parm("delete_plant_state").set(False)

def state_mode_changed(kwargs):
    print("state_mode changed")
    json_parm = kwargs["node"].parm("terrain_json")
    json_str = json_parm.evalAsString()
    if(json_str.strip() == ""):
        json_parm.set(generate_terrain_json(kwargs))

def change_placement_mode_callback(kwargs):
    # get current node
    knode = kwargs["node"]
    
    # maps placement mode to state mode
    mode_mapping = {
    "point":"plant_point",
    "draw":"plant_draw",
    "edit":"plant_edit_selection",
    "delete":"plant_delete",
    }
    # stash previous changes
    stash(kwargs)
    # set state mode
    knode.parm("state_mode").set(mode_mapping[knode.parm("place_mode").evalAsString()])
    
def reset_dist_parms(kwargs):
    knode = kwargs["node"]
    knode.parm("plants_stroke_numstrokes").set(0)
    knode.parm("points").set(0)
    knode.setParms({
                        "edit_mode_pivotx":0,"edit_mode_pivoty":0,"edit_mode_pivotz":0,
                        "edit_mode_translatex":0, "edit_mode_translatey":0, "edit_mode_translatez":0,
                        "edit_mode_rotatex":0, "edit_mode_rotatey":0, "edit_mode_rotatez":0},)

def generate_terrain_json(kwargs):
    knode = kwargs["node"]
    platform_prims = knode.node("draw_terrain/OUT_viewer_terrain_platforms_collision").geometry().prims()
    json_list = list()
    for prim in platform_prims:
        json_handle = dict()
        json_handle["height"] = 0
        json_handle["smoothness"] = 0
        json_list.append(json_handle)
    
    json_value = json.dumps(json_list)
    return json_value

def clearGeo(kwargs):
    knode = kwargs["node"]
    knode.parm("stash_clear_toggle").set(1)
    knode.parm("stash_plant_points").pressButton()
    knode.parm("stash_clear_toggle").set(0)
    reset_dist_parms(kwargs)

def create_temp_dir(kwargs):
    knode = kwargs["node"]

    temp_dir_path = tempfile.mkdtemp(prefix="parker_garden_builder")
    knode.parm("tmp_dir").set(temp_dir_path)

def render_thumbnail(kwargs):
    knode = kwargs["node"]

    tmp_dir = knode.parm("tmp_dir").evalAsString()
    if(not os.path.exists(tmp_dir)):
        print(f"temp dir doesn't exist '{tmp_dir}', creating new temp dir")
        create_temp_dir(kwargs)
    knode.parm("plant_render_thumbnail/lopnet/render_thumbnail/execute").pressButton()

    

