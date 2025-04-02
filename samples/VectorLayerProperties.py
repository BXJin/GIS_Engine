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

class VectorLayerProperties(QMainWindow):
    def __init__(self):
        super().__init__()

        layer = list(
            filter(
                lambda l: isinstance(l, QgsVectorLayer) and l.name() == "벡터 레이어", 
                QgsProject.instance().mapLayers().values()
            )
        )

        self.dlg = QgsVectorLayerProperties(canvas = QgsMapCanvas(),
                                            lyr = layer[0], 
                                            messageBar=QgsMessageBar(), 
                                            parent=self)
        # self.dlg.show()

    def show(self):
        self.dlg.show()

