from PySide2 import QtWidgets, QtGui, QtCore
import hou
import math

class OverlappingNavigationBarLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, overlap=10, start_x=0):
        super().__init__(parent)
        self.overlap = overlap
        self.start_x = start_x/2
        self.item_list = []

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if(0 <= index < len(self.item_list)):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if(0 <= index < len(self.item_list)):
            return self.item_list.pop(index)
        return None

    def sizeHint(self):
        total_width = 0
        max_height = 0
        for item in self.item_list:
            size = item.sizeHint()
            total_width += size.width()
            max_height = max(max_height, size.height())
        return QtCore.QSize(total_width, max_height)

    def setGeometry(self, rect):
        x = rect.x()+self.start_x
        y = rect.y()
        for item in self.item_list:
            widget = item.widget()
            widget.lower() # place each item below the previous
            if widget is not None and widget.isVisible():
                size = widget.sizeHint()
                item_rect = QtCore.QRect(
                    x, y, size.width(), rect.height()
                )
                item.setGeometry(item_rect)
                x += size.width() - self.overlap
            else:
                print("skipping item:", widget.text())

    def expandingDirections(self):
        return QtCore.Qt.Horizontal



class NavigationBarButton(QtWidgets.QPushButton):
    def __init__(self, page, index, parent, bar):
        page_name = page
        super().__init__(page_name.title(), parent)

        self.page = page
        self.parent = parent
        self.index = index

        self.setFixedHeight(bar.bar_height-bar.border_width)

        self.setVisible(True)

        bg_color = hou.qt.getColor("ButtonGradLow").name()
        bg_color_alt = hou.qt.getColor("TreeNodeAlternateBG").name()

        # bg_color = "red"
        # bg_color_alt = "green"

        bg_color = bg_color if self.index%2==0 else bg_color_alt
        color_pressed = hou.qt.getColor("ButtonPressedGradHi").name()
        border_radius = 11

        style_sheet = None
        if(index==0):
            # bg_color="red"
            style_sheet = (f"QPushButton {{background-color:{bg_color}; border-radius: {border_radius};}}"+
                           f"QPushButton::pressed {{background-color:{color_pressed}; border-radius: {border_radius}; }}")
        else:
            # bg_color="green"
            style_sheet = (f"QPushButton {{background-color:{bg_color}; border-top-right-radius: {border_radius}; border-bottom-right-radius: {border_radius}; }}"+
                   f"QPushButton::pressed {{background-color:{color_pressed}; border-top-right-radius: {border_radius}; border-bottom-right-radius: {border_radius}; }}")

        self.setStyleSheet(style_sheet)

        self.clicked.connect(self.onClicked)

    def onClicked(self):
        print("HERE: page_clicked", self.index)
        



class NavigationBar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.bar_height = 30
        self.border_width = 2


        self.main_layout = QtWidgets.QHBoxLayout()
        self.page_layout = OverlappingNavigationBarLayout(overlap=10, start_x=self.border_width)
        # self.page_layout = QtWidgets.QVBoxLayout()

        self.background_widget = QtWidgets.QWidget()
        self.main_layout.addWidget(self.background_widget)
        self.background_widget.setLayout(self.page_layout)

        bg_color = hou.qt.getColor("ButtonGradLow").name()
        self.background_widget.setObjectName("NavigationBarBorder")
        self.background_widget.setStyleSheet(f"QWidget#NavigationBarBorder{{ background-color: {bg_color}; border-radius: 9;}}")
        self.background_widget.setMaximumHeight(30)
        self.main_layout.setContentsMargins(0,0,0,0)


        self.pages = []

        self.current_page_indx = 0
        self.current_page = None

        self.setLayout(self.main_layout)

    # def _pages_updated(self):
    #     pass

    def add_page(self, page_name):
        page_indx = len(self.pages)
        new_page = NavigationBarButton(page_name, page_indx, parent=self.background_widget, bar=self)
        self.pages.append(new_page)

        self.page_layout.addWidget(new_page)



        # self.current_page = new_page
        # self.current_page_indx = page_indx

    def page_forward(self):
        if(self.current_page_indx+1>len(self.pages)-1):
            print("page_backward: can't go forwards any further")
            return
        self.set_page(self.current_page_indx+1)

    def page_backward(self):
        if(self.current_page_indx-1<0):
            print("page_backward: can't go backwards any further")
            return
        self.set_page(self.current_page_indx-1)

    def clear_pages(self):
        self.current_page_indx = 0
        self.current_page = None
        self.pages.clear()
        widgets = []
        for i in range(self.page_layout.count()):
            widget = self.page_layout.itemAt(i).widget()
            widgets.append(widget)

        for widget in widgets:
            self.page_layout.removeWidget(widget)
            widget.deleteLater()
        # self.pages.pop()



    def remove_page(self, index):
        pass


    def set_page(self, index):
        if(index == self.current_page_indx):
            print("doing nothing")
            return

        prev_indx = self.current_page_indx
        self.current_page_indx = index

        print("from indx:", prev_indx)
        print("to indx:", self.current_page_indx)

        traversal_direction = int(math.copysign(1, self.current_page_indx-prev_indx))
        if(not (traversal_direction==-1 or traversal_direction==1)):
            raise Exception("unexpected traversal direction:", traversal_direction)

        print('direction:', traversal_direction)

        traversal_count = abs(prev_indx-self.current_page_indx)
        print("count:", traversal_count)
        for i in range(traversal_count):
            forward_offset = 1 if traversal_direction==1 else 0
            widget_indx = prev_indx+((i+forward_offset)*traversal_direction)
            print("showing indx:", widget_indx)
            widget = self.pages[widget_indx]
            widget.setVisible(traversal_direction==1)

            # self.pages.pop()
            # self.main_layout.removeWidget(widget)
            # widget.deleteLater()

