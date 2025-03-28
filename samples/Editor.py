import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter, QFrame, QToolBar, QAction
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from qgis.core import (
    QgsApplication, QgsProject, QgsLayerTreeModel,
    QgsVectorLayer, QgsRasterLayer, Qgis, QgsLayerTree,
)
from qgis.gui import QgsMapCanvas, QgsLayerTreeView, QgsBrowserTreeView, QgsBrowserGuiModel, QgsLayerTreeMapCanvasBridge, QgsVertexTool, QgsMapToolEdit


class Editor(QMainWindow):
    def __init__(self):
        super().__init__()

        print("version : " + Qgis.version())

        # 🟢 QGIS 환경 초기화
        self.qgs = QgsApplication([], True)
        self.project = QgsProject.instance()
        self.qgs.initQgis()

        # UI 초기화
        self.initUI()

        # 샘플 레이어 불러오기
        self.loadLayers()


    def initUI(self):
        self.setWindowTitle("QGIS Standalone App with Editing")
        self.setGeometry(100, 100, 1400, 800)

        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 🔹 메인 Splitter 생성 (좌측 탐색기 + TOC / 우측 지도 캔버스)
        main_splitter = QSplitter()
        layout.addWidget(main_splitter)

        # 🔹 좌측 패널 (탐색기 + TOC)
        left_panel = QSplitter(Qt.Vertical)
        left_panel.setFrameShape(QFrame.StyledPanel)
        main_splitter.addWidget(left_panel)

        # 🟢 탐색기 패널 추가 (QgsBrowserTreeView)
        self.browser_model = QgsBrowserGuiModel()
        self.browser_model.initialize()
        self.browser_model.refresh()
        self.browser_tree = QgsBrowserTreeView()
        self.browser_tree.setModel(self.browser_model)
        self.browser_tree.doubleClicked.connect(self.loadSelectedLayer)
        left_panel.addWidget(self.browser_tree)

        # 🟢 레이어 목록 (TOC) 추가 (QgsLayerTreeView)
        self.layer_tree = QgsLayerTreeView()
        self.layer_tree_model = QgsLayerTreeModel(self.project.layerTreeRoot())
        self.layer_tree_model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)
        self.layer_tree_model.setFlag(QgsLayerTreeModel.AllowNodeReorder)
        self.layer_tree.setModel(self.layer_tree_model)
        left_panel.addWidget(self.layer_tree)

        # 🟢 지도 캔버스 추가
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor("white"))
        main_splitter.addWidget(self.canvas)

        # 🚀 지도 캔버스와 레이어 트리 연결
        self.bridge = QgsLayerTreeMapCanvasBridge(self.project.layerTreeRoot(), self.canvas)
        self.bridge.autoSetupOnFirstLayer()

        # 🔹 편집 툴바 추가
        self.initToolbar()

    def initToolbar(self):
        """ 편집 기능을 위한 툴바 추가 """
        self.toolbar = QToolBar("편집 도구")
        self.addToolBar(self.toolbar)

        # 🟢 편집 모드 버튼 추가
        self.edit_action = QAction("편집 모드", self)
        self.edit_action.setCheckable(True)
        self.edit_action.toggled.connect(self.toggleEditing)
        self.toolbar.addAction(self.edit_action)

        # 🟢 정점 편집 버튼 추가
        self.vertex_edit_action = QAction("정점 편집", self)
        self.vertex_edit_action.setCheckable(True)
        self.vertex_edit_action.toggled.connect(self.toggleVertexEditing)
        self.toolbar.addAction(self.vertex_edit_action)

        # 🟢 편집 저장 버튼 추가
        self.save_action = QAction("저장", self)
        self.save_action.triggered.connect(self.saveEdits)
        self.toolbar.addAction(self.save_action)

        # 🟢 편집 취소 버튼 추가
        self.cancel_action = QAction("취소", self)
        self.cancel_action.triggered.connect(self.cancelEdits)
        self.toolbar.addAction(self.cancel_action)

        # 🟢 편집 도구 초기화
        self.edit_tool = QgsMapToolEdit(self.canvas)
        self.vertex_tool = QgsVertexTool(self.canvas)

    def toggleEditing(self, checked):
        """ 편집 모드 토글 """
        if checked:
            self.canvas.setMapTool(self.edit_tool)
            print("✅ 편집 모드 활성화")
        else:
            self.canvas.unsetMapTool(self.edit_tool)
            print("❌ 편집 모드 비활성화")

    def toggleVertexEditing(self, checked):
        """ 정점 편집 모드 토글 """
        if checked:
            self.canvas.setMapTool(self.vertex_tool)
            print("✅ 정점 편집 모드 활성화")
        else:
            self.canvas.unsetMapTool(self.vertex_tool)
            print("❌ 정점 편집 모드 비활성화")

    def saveEdits(self):
        """ 편집 저장 """
        for layer in self.project.mapLayers().values():
            if layer.isEditable():
                layer.commitChanges()
        print("✅ 편집 내용 저장 완료")

    def cancelEdits(self):
        """ 편집 취소 """
        for layer in self.project.mapLayers().values():
            if layer.isEditable():
                layer.rollBack()
        print("❌ 편집 내용 취소됨")

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
            print(f"✅ {file_path} 레이어 추가됨")
        else:
            print(f"❌ {file_path} 레이어를 불러올 수 없음")

    def closeEvent(self, event):
        """ 창을 닫을 때 QGIS 종료 """
        self.qgs.exitQgis()
        event.accept()

