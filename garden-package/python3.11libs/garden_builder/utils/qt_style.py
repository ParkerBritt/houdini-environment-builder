import hou

def set_valid(widget, is_valid):
    widget.setProperty("invalid", not is_valid)
    widget.style().polish(widget)


class QT_Style:
    @staticmethod
    def _initialize_style_sheet():
        use_houdini_colors = True

        cl_bg_dark = "#201F1F"
        cl_bg_mid = "#2b2a2a"
        cl_bg_accent = "#2F4A14"
        cl_selected = "#4E8634"
        cl_selected_alt = "#5a983b"
        cl_selected_hover = "#6d9d59"

        cl_bttn_hover = "#363535"

        cl_list_alt = "#313131"
        invalid_color = "#ff8c8c"

        if(use_houdini_colors):
            cl_bg_dark = hou.qt.getColor("BackColor").name()
            # cl_bg_dark = hou.qt.getColor("TreeNodeAlternateBG").name()

        return (
            f"QWidget#MainBackground{{background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {cl_bg_accent}, stop:0.2 {cl_bg_dark}); border-radius: 0px;}}"
            f"QWidget {{ background-color: {cl_bg_mid}; border-radius: 10px; }}"
            f"QLineEdit {{ border-radius: 10px ; padding: 4px 5px; }}"
            f"QComboBox::drop-down {{ background-color: {cl_bg_dark}; border-radius: 8px ; }}"
            f"QComboBox::drop-down:hover {{ background-color: {cl_bttn_hover}; border-radius: 8px ; }}"
            f"QComboBox::down-arrow {{ color: white; image: url(:images/icons/down_arrow_8x.png);}}"

            f"QWidget#PageContainer {{ background-color: transparent; }}"

            f"#PageContainer {{background-color: {'#2b2a2a'}; border-radius: 20px;}}"
            f"QPushButton {{background-color: {'#202020'}; border-radius: 10px;}}"


            f"QListWidget{{border-radius: 15px; border: none;}}"
            f"QListWidget::item{{border-radius: 9px; margin: 1; padding: 3;}}"
            f"QListWidget::item:selected{{background-color: {cl_selected};}}"
            f"QListWidget::item:selected:alternate{{background: {cl_selected_alt};}}"
            f"QListWidget::item:alternate{{background-color: {cl_list_alt};}}"

            f"QWidget[dark_background=\"true\"] {{ background-color: {cl_bg_dark};}}"
            f"QWidget[mid_background=\"true\"] {{ background-color: {cl_bg_mid};}}"
            f"QWidget[transparent_background=\"true\"] {{ background-color: transparent;}}"
            f"QLineEdit[invalid=\"true\"] {{ border: 2px solid {invalid_color}; }}"

            f"QPushButton:checked {{background-color: {cl_selected};}}"
            f"QPushButton:hover {{background-color: {cl_bttn_hover};}}"
            f"QPushButton:checked:hover {{background-color: {cl_selected_hover};}}"
        )

    _style_sheet = _initialize_style_sheet()

    def __init__(self):
        pass

    def get_style_sheet():
        return QT_Style._style_sheet
