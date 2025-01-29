from PySide2 import QtWidgets, QtGui, QtCore

def round_pixmap_corners(in_pixmap):
    canvas = QtGui.QPixmap(in_pixmap.size())
    canvas.fill(QtCore.Qt.transparent)

    painter = QtGui.QPainter(canvas)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)

    corner_radius = 15

    path = QtGui.QPainterPath()
    rect = QtCore.QRectF(0,0, canvas.width(), canvas.height())
    path.addRoundedRect(rect, corner_radius, corner_radius)

    painter.setClipPath(path)

    painter.drawPixmap(0, 0, in_pixmap)
    painter.end()

    return canvas

def add_text(in_pixmap, text, x=0, y=0, font_size=20):
    painter = QtGui.QPainter(in_pixmap)

    font = painter.font()
    font.setPointSize(font_size)
    painter.setFont(font)
    painter.setPen(QtGui.QColor("white"))
    painter.drawText(x,y, text)
    painter.end()

    return in_pixmap
