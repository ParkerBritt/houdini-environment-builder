class PlantRegistry():
    def __init__(self, list_widget):
        self._plant_list = []

    def add_plant(self, plant):
        self._plant_list.append(plant)
    
    def get_plants(self):
        return self._plant_list

    def clear(self):
        self._plant_list.clear()
