from enum import Enum

class ViewerMode():
    # Plant
    PLANT_PLACE = 0
    PLANT_DRAW = 1
    PLANT_EDIT_SELECTION = 2
    PLANT_EDIT_HANDLE = 3  
    PLANT_ERASE = 4

    # Terrain
    TERRAIN_DRAW = 5
    TERRAIN_SELECT = 6
    TERRAIN_DELETE = 7

    # Water
    WATER_CURVE = 8
    WATER_REGION = 9
    WATER_DELETE = 10

    INACTIVE = 11

    mode_map = {
        "inactive":INACTIVE,

        "plant_point":PLANT_PLACE,
        "plant_draw":PLANT_DRAW,
        "plant_edit_selection":PLANT_EDIT_SELECTION,
        "plant_edit_handle":PLANT_EDIT_HANDLE,
        "plant_delete":PLANT_ERASE,

        "terrain_draw":TERRAIN_DRAW,
        "terrain_select":TERRAIN_SELECT,
        "terrain_delete":TERRAIN_DELETE,

        "water_curve":WATER_CURVE,
        "water_region":WATER_REGION,
        "water_delete":WATER_DELETE,
    }
    
    name_map = {v : k for k, v in mode_map.items()}

    @staticmethod
    def map_state(mode_name):
        """Maps input string to a returned ViewerMode enum"""

        if(isinstance(mode_name, str)):
            if(mode_name not in ViewerMode.mode_map):
                raise Exception(f"mode: {mode_name} not in mode map: {ViewerMode.mode_map}")
            return ViewerMode.mode_map[mode_name]

        elif(isinstance(mode_name, int)):
            if(mode_name not in ViewerMode.name_map):
                raise Exception(f"mode: {mode_name} not in mode map: {ViewerMode.name_map}")
            return ViewerMode.name_map[mode_name]



