import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget
from qgis.core import *
from qgis.gui import QgsMapCanvas
from PyQt5.QtGui import QColor

class LoadLayer(QMainWindow):
    def __init__(self):
        super().__init__()

        # QGIS 환경 초기화
        self.qgs = QgsApplication([], False)
        self.qgs.initQgis()

        # UI 초기화
        self.initUI()

    def initUI(self):
        self.setWindowTitle("QGIS PyQt Map Viewer")
        self.setGeometry(100, 100, 800, 600)

        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 레이아웃 설정
        layout = QVBoxLayout(central_widget)

        # QGIS 지도 캔버스 생성
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor("white"))
        layout.addWidget(self.canvas)

        # 레이어 추가 버튼
        self.button = QPushButton("레이어 추가", self)
        self.button.clicked.connect(self.load_layer)
        layout.addWidget(self.button)

    def load_layer(self):
        # 벡터 파일 선택
        file_path, _ = QFileDialog.getOpenFileName(self, "벡터 파일 선택", "", "Shapefiles (*.shp);;GeoJSON (*.geojson);;All Files (*)")
        if not file_path:
            return

        # 벡터 레이어 로드
        layer = QgsVectorLayer(file_path, "Loaded Layer", "ogr")
        if not layer.isValid():
            print("레이어 로딩 실패!")
            return
        
        # 지도에 추가
        QgsProject.instance().addMapLayer(layer)
        self.canvas.setLayers([layer])
        self.canvas.zoomToFullExtent()

    def closeEvent(self, event):
        """ 창을 닫을 때 QGIS 종료 """
        self.qgs.exitQgis()
        event.accept()
