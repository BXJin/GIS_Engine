import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter, QFrame
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from qgis.core import (
    QgsApplication, QgsProject, QgsLayerTreeModel,
    QgsVectorLayer, QgsRasterLayer, Qgis,
    QgsFileUtils, QgsLayerTree, QgsLayerTreeLayer, QgsLayerTreeGroup
)
from qgis.gui import QgsMapCanvas, QgsLayerTreeView, QgsBrowserTreeView, QgsBrowserGuiModel, QgsLayerTreeMapCanvasBridge

class LayerOrder(QMainWindow):
    def __init__(self):
        super().__init__()

        print("version : " + Qgis.version())
        
        # 🟢 QGIS 환경 초기화
        self.qgs = QgsApplication([], True)

        # 프로젝트 생성
        self.project = QgsProject.instance()

        self.qgs.initQgis()

        # UI 초기화
        self.initUI()

        # 샘플 레이어 불러오기
        self.loadLayers()


    def initUI(self):
        self.setWindowTitle("QGIS Standalone App with Browser & TOC")
        self.setGeometry(100, 100, 1400, 800)

        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 전체 레이아웃 설정
        layout = QVBoxLayout(central_widget)

        # 🔹 메인 Splitter 생성 (좌측 탐색기 + TOC / 우측 지도 캔버스)
        main_splitter = QSplitter()
        layout.addWidget(main_splitter)

        # 🔹 좌측 패널 (탐색기 + TOC)
        left_panel = QSplitter()
        left_panel.setOrientation(2)  # 수직 방향 (Qt.Vertical)
        left_panel.setFrameShape(QFrame.StyledPanel)
        main_splitter.addWidget(left_panel)

        # 🟢 탐색기 패널 추가 (QgsBrowserTreeView)
        self.browser_model = QgsBrowserGuiModel()
        self.browser_model.initialize()
        # self.browser_model = SimpleCustomBrowserModel()
        self.browser_model.refresh()  # 🚀 탐색기 데이터 갱신
        self.browser_tree = QgsBrowserTreeView()
        self.browser_tree.setModel(self.browser_model)
        self.browser_tree.doubleClicked.connect(self.loadSelectedLayer)  # 🟢 더블 클릭 이벤트
        # self.browser_tree.set
        left_panel.addWidget(self.browser_tree)

        # 🟢 레이어 목록 (TOC) 추가 (QgsLayerTreeView)
        self.layer_tree = QgsLayerTreeView()
        self.layer_tree_model = QgsLayerTreeModel(self.project.layerTreeRoot())
        self.layer_tree_model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)
        self.layer_tree_model.setFlag(QgsLayerTreeModel.AllowNodeReorder)
        self.layer_tree.setModel(self.layer_tree_model)
        left_panel.addWidget(self.layer_tree)

        # 🚀 레이어 트리 뷰의 시그널을 캔버스에 연결        
        # self.project.layersAdded.connect(self.layersAdded)
        # self.project.layersRemoved.connect(self.layersRemoved)
        # self.project.layerTreeRoot().layerOrderChanged.connect(self.layerOrderChanged)
        # self.project.layerTreeRoot().visibilityChanged.connect(self.visibilityChanged)

        
        # 🟢 지도 캔버스 추가
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor("white"))
        main_splitter.addWidget(self.canvas)

        # 크기 조정 비율 설정
        main_splitter.setStretchFactor(0, 1)  # 좌측 패널 (탐색기 + TOC)
        main_splitter.setStretchFactor(1, 3)  # 우측 지도 캔버스

        self.bridge = QgsLayerTreeMapCanvasBridge(self.project.layerTreeRoot(), self.canvas)
        self.bridge.autoSetupOnFirstLayer()

    def visibilityChanged(self, node):
        """ 체크박스 상태 변경 시 호출되는 핸들러 """
        print(f"레이어 가시성 변경: {node.name()} -> {node.isVisible()}")
        self.canvas.refresh()

    def layersAdded(self, layers):
        """ 레이어가 추가될 때 호출되는 핸들러 """
        print(f"레이어 추가됨: {[layer.name() for layer in layers]}")
        
        # 추가된 레이어를 캔버스에 반영
        self.canvas.setLayers(self.project.mapLayers().values())

    def layersRemoved(self, layer_ids):
        """ 레이어가 제거될 때 호출되는 핸들러 """
        print(f"레이어 제거됨: {layer_ids}")
        # 추가된 레이어를 캔버스에 반영
        self.canvas.setLayers(self.project.mapLayers().values())

    def layerOrderChanged(self):
        """ 레이어 순서가 변경될 때 호출되는 핸들러 """
        print("레이어 순서 변경됨")
        
        # 레이어 트리에서 현재 순서대로 레이어 목록 가져오기
        root = self.project.layerTreeRoot()
        ordered_layers = []
        
        # 재귀적으로 레이어 순서 수집
        def collect_layers(node):
            if QgsLayerTree.isLayer(node):  # 정적 메서드로 호출
                ordered_layers.append(node.layer())
            elif QgsLayerTree.isGroup(node):  # 정적 메서드로 호출
                for child in node.children():
                    collect_layers(child)
    
        collect_layers(root)
        
        # 캔버스 레이어 순서 업데이트
        self.canvas.setLayers(ordered_layers)
        self.canvas.refresh()
        
        
    def loadLayers(self):
        """ 🟢 샘플 벡터 및 래스터 레이어 추가 """
        shape = "test/ctprvn_20230729/ctprvn.shp"
        vector_layer = QgsVectorLayer(shape, "벡터 레이어", "ogr")
        if vector_layer.isValid():
            self.project.addMapLayer(vector_layer)

        raster_layer = QgsRasterLayer("test/sample.tif", "래스터 레이어", "gdal")
        if raster_layer.isValid():
            self.project.addMapLayer(raster_layer)

        # ✅ 지도 캔버스에 추가된 레이어 설정
        self.canvas.setLayers(self.project.mapLayers().values())
        self.canvas.zoomToFullExtent()

    def loadSelectedLayer(self, index):
        """ 🟢 브라우저에서 선택한 파일을 불러오는 함수 """
        self.browser_model.data
        # file_path = self.browser_model.filePath(index)
        file_path = self.browser_model.data(index, Qt.UserRole)

        print(f"선택된 파일: {file_path}")

        if file_path.lower().endswith(".shp"):
            layer = QgsVectorLayer(file_path, "벡터 레이어", "ogr")
        elif file_path.lower().endswith((".tif", ".tiff")):
            layer = QgsRasterLayer(file_path, "래스터 레이어", "gdal")
        else:
            print("지원되지 않는 파일 유형:", file_path)
            return

        if layer.isValid():
            self.project.addMapLayer(layer)
            self.canvas.setLayers(self.project.mapLayers().values())

            # self.canvas.zoomToFullExtent()
            print(f"✅ {file_path} 레이어 추가됨")
        else:
            print(f"❌ {file_path} 레이어를 불러올 수 없음")

    def closeEvent(self, event):
        """ 창을 닫을 때 QGIS 종료 """
        self.qgs.exitQgis()
        event.accept()

    def updateCanvasLayers(self):
        """ 🟢 레이어 순서 변경 시 캔버스 레이어 업데이트 """
        root = self.project.layerTreeRoot()
        layers = [layer.layer() for layer in root.children()]
        self.canvas.setLayers(layers)
        self.canvas.refresh()
