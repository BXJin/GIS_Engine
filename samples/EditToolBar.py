from qgis.PyQt.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsApplication, QgsVectorLayer, QgsFeature, QgsPointXY, QgsProject, QgsGeometry, QgsWkbTypes
    ,QgsRendererRange, QgsFillSymbol, QgsSymbol
)
from qgis.gui import (
    QgsMapCanvas, QgsMapToolEmitPoint, QgsMapToolDigitizeFeature, QgsAdvancedDigitizingDockWidget # QgsAdvancedDigitizingDockWidget 추가
    ,QgsMapToolCapture
)
from qgis.PyQt.QtCore import Qt

class EditToolBar(QMainWindow):
    def __init__(self):
        super().__init__()

        # QGIS 맵 캔버스 추가
        self.canvas = QgsMapCanvas()
        self.setCentralWidget(self.canvas)

        # 벡터 레이어 생성 및 추가
        self.layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "편집 레이어", "memory")

        # 레이어 스타일 설정 (빨간색 채우기)
        symbol = QgsFillSymbol.createSimple({'color': '255,0,0,255'})
        renderer = self.layer.renderer()
        if renderer:
            renderer.setSymbol(symbol)
        else:
            single_symbol_renderer = QgsRendererRange.createRenderer(self.layer.geometryType(), symbol)
            self.layer.setRenderer(single_symbol_renderer)

        QgsProject.instance().addMapLayer(self.layer)
        self.canvas.setLayers([self.layer])
        self.canvas.setExtent(self.layer.extent())
        self.canvas.refresh()

        # 고급 디지타이징 독 위젯 생성
        self.adv_digitizing_dock_widget = QgsAdvancedDigitizingDockWidget(self.canvas)
        self.addDockWidget(Qt.RightDockWidgetArea, self.adv_digitizing_dock_widget) # 독 위젯을 메인 윈도우에 추가 (선택 사항)

        # 디지털화 도구 초기화
        self.digitize_tool = None

        # 편집 툴바 생성
        self.edit_toolbar = QToolBar("편집 도구")
        self.addToolBar(self.edit_toolbar)

        # QAction 추가
        self.add_edit_actions()

        # 윈도우 설정
        self.setWindowTitle("QGIS 편집 툴바 (고급 디지타이징)")
        self.resize(800, 600)

    def add_edit_actions(self):
        """mEditingToolBar의 주요 QAction을 추가"""
        actions = [
            (":/mActionToggleEditing.svg", "편집 모드 토글", self.toggle_editing),
            (":/edit_add.svg", "새 폴리곤 그리기 (고급)", self.enable_digitizing_advanced), # 텍스트 변경
            (":/edit_remove.svg", "피처 삭제", self.delete_feature),
        ]

        for icon_path, text, callback in actions:
            action = QAction(QIcon(icon_path), text, self)
            action.triggered.connect(callback)
            self.edit_toolbar.addAction(action)

    def toggle_editing(self):
        """편집 모드 토글"""
        if self.layer.isEditable():
            self.layer.commitChanges()  # 편집 모드 종료
            QMessageBox.information(self, "편집 모드", "편집 모드를 종료했습니다.")
            self.disable_digitizing()
        else:
            self.layer.startEditing()  # 편집 모드 시작
            QMessageBox.information(self, "편집 모드", "편집 모드를 시작했습니다.")

    def enable_digitizing_advanced(self):
        """새 폴리곤 그리기 모드 활성화 (고급)"""
        if not self.layer.isEditable():
            QMessageBox.warning(self, "오류", "편집 모드를 먼저 활성화하세요.")
            return
        if self.digitize_tool is None:
            # 고급 디지타이징 독 위젯을 인수로 전달
            self.digitize_tool = QgsMapToolDigitizeFeature(
                self.canvas,
                self.adv_digitizing_dock_widget,
                QgsMapToolCapture.CapturePolygon,
            )
            self.digitize_tool.setLayer(self.layer)
            self.digitize_tool.digitizingCompleted.connect(self.add_digitized_feature) # 시그널 연결

        self.canvas.setMapTool(self.digitize_tool)
        QMessageBox.information(self, "폴리곤 그리기 (고급)", "마우스로 클릭하여 폴리곤을 그리고, 우클릭으로 완료하세요. 고급 디지타이징 패널을 확인하세요.")

    def disable_digitizing(self):
        """디지털화 도구 비활성화"""
        if self.digitize_tool and self.canvas.mapTool() == self.digitize_tool:
            self.canvas.unsetMapTool(self.digitize_tool)

    def add_digitized_feature(self, feature):
        """디지털화된 피처를 레이어에 추가"""
        self.layer.addFeature(feature)
        self.layer.updateExtents()
        self.layer.triggerRepaint()
        self.canvas.setExtent(self.layer.extent())
        self.canvas.refresh()

    def delete_feature(self):
        """모든 피처 삭제"""
        if not self.layer.isEditable():
            QMessageBox.warning(self, "오류", "편집 모드를 먼저 활성화하세요.")
            return

        for feature in self.layer.getFeatures():
            self.layer.deleteFeature(feature.id())

        self.layer.triggerRepaint()
        self.canvas.refresh()