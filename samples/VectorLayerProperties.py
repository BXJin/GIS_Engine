from qgis.PyQt.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsApplication, QgsVectorLayer, QgsFeature, QgsPointXY, QgsProject, QgsGeometry, QgsWkbTypes
    ,QgsRendererRange, QgsFillSymbol, QgsSymbol
)
from qgis.gui import (
    QgsMapCanvas, QgsMapToolEmitPoint, QgsMapToolDigitizeFeature, QgsAdvancedDigitizingDockWidget # QgsAdvancedDigitizingDockWidget 추가
    ,QgsMapToolCapture, QgsVectorLayerProperties, QgsMessageBar
)
from qgis.PyQt.QtCore import Qt
from geon.layer import getLayerByName

class VectorLayerProperties(QMainWindow):
    def __init__(self):
        super().__init__()

        layer = getLayerByName("벡터 레이어")

        self.dlg = QgsVectorLayerProperties(canvas = QgsMapCanvas(),
                                            lyr = layer, 
                                            messageBar=QgsMessageBar(), 
                                            parent=self)

    def show(self):
        self.dlg.show()

