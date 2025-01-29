from PySide2 import QtWidgets, QtGui
import hou

class NavigationButtons(QtWidgets.QWidget):
    def __init__(self, navigation_bar):
        super().__init__()
        self.navigation_bar = navigation_bar
        self.initUI()

    def initUI(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.back_button = QtWidgets.QPushButton("<")
        back_font = self.back_button.font()
        # back_font.setPointSize(15)
        back_font.setBold(True)
        self.back_button.setFont(back_font)
        self.back_button.setMaximumWidth(30)

        bg_color = hou.qt.getColor("ButtonGradLow").name()
        color_pressed = hou.qt.getColor("ButtonPressedGradHi").name()
        button_style_sheet = (f"QPushButton {{background-color:{bg_color}; border-radius: 7; padding: 5 10 5 10;}}"+
                   f"QPushButton::pressed {{background-color:{color_pressed}; border-radius: 10;}}")

        self.forward_button = QtWidgets.QPushButton(">")
        self.forward_button.setMaximumWidth(30)
        self.main_layout.addWidget(self.back_button)
        self.forward_button.setFont(back_font)
        self.main_layout.addWidget(self.forward_button)
        self.forward_button.setStyleSheet(button_style_sheet)

        self.forward_button.clicked.connect(self.onForwardClicked)
        self.back_button.clicked.connect(self.onBackClicked)
        self.back_button.setStyleSheet(button_style_sheet)

        # color_pressed = hou.qt.getColor("ButtonPressedGradHi").name()
        # bg_color = hou.qt.getColor("ButtonGradLow").name()
        # style_sheet = (f"QPushButton {{background-color:{bg_color}; border-radius: 10;}}"+
        #                f"QPushButton::pressed {{background-color:{color_pressed}; border-radius: 10; }}")
        # self.forward_button.setStyleSheet(style_sheet)


        self.setLayout(self.main_layout)

    def onForwardClicked(self):
        self.navigation_bar.page_forward()

    def onBackClicked(self):
        self.navigation_bar.page_backward()
