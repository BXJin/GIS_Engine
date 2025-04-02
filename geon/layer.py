from qgis.PyQt.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsApplication, QgsVectorLayer, QgsFeature, QgsPointXY, QgsProject, QgsGeometry, QgsWkbTypes
    ,QgsRendererRange, QgsFillSymbol, QgsSymbol
    , QgsMapLayer
)
from qgis.gui import (
    QgsMapCanvas, QgsMapToolEmitPoint, QgsMapToolDigitizeFeature, QgsAdvancedDigitizingDockWidget # QgsAdvancedDigitizingDockWidget 추가
    ,QgsMapToolCapture, QgsVectorLayerProperties, QgsMessageBar
)
from typing import Callable, List
from geon.utils import IterableUtils

def where(predicate: Callable[[QgsMapLayer], bool] = lambda l: True) -> List[QgsMapLayer]:
    """
    주어진 조건(predicate)을 만족하는 모든 레이어를 반환.

    :param predicate: 레이어 필터링을 위한 함수 (기본값: 항상 True)
    :return: 조건을 만족하는 레이어 리스트
    """
    return [layer for layer in QgsProject.instance().mapLayers().values() if predicate(layer)]

def getLayerByName(layer_name: str):
    """
    """
    layers = where(lambda layer:  layer.name() == layer_name)
    return IterableUtils.first(layers)

