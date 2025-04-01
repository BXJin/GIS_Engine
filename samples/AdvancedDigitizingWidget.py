from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from qgis.core import (
    QgsApplication, QgsProject, QgsVectorLayer, QgsFeatureRequest, 
    QgsSnappingConfig
)
from qgis.gui import (
    QgsMapCanvas, QgsMapToolEdit, QgsAdvancedDigitizingDockWidget, 
    QgsMapToolIdentifyFeature, QgsSnapIndicator
)

from samples.VertexEditTool import VertexEditTool

class AdvancedDigitizingWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.qgs = QgsApplication([], True)
        self.qgs.initQgis()

        self.project = QgsProject.instance()
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor("white"))
        self.setCentralWidget(self.canvas)

        self.initUI()
        self.initAdvancedDigitizing()
        self.loadVectorLayer()

        self.select_tool = QgsMapToolIdentifyFeature(self.canvas, self.vector_layer)
        self.select_tool.featureIdentified.connect(self.featureIdentified)
        self.setMapTool(self.select_tool)
        self.edit_tool = QgsMapToolEdit(self.canvas)
        self.snap_indicator = QgsSnapIndicator(self.canvas)
        
        # 버텍스 편집 도구
        self.vertex_tool = None
        
        # 마우스 이동 이벤트 연결
        self.canvas.xyCoordinates.connect(self.onMouseMove)
        
        config = QgsSnappingConfig()
        config.setEnabled(True)
        config.setTolerance(10)
        config.setType(QgsSnappingConfig.VertexAndSegment)
        
        # 개별 레이어 설정
        layer_settings = QgsSnappingConfig.IndividualLayerSettings()
        layer_settings.setEnabled(True)  # 레이어별 스냅핑 활성화
        layer_settings.setType(QgsSnappingConfig.VertexAndSegment)  # 버텍스와 세그먼트 스냅핑
        layer_settings.setTolerance(10)  # 스냅핑 거리 (픽셀)

        # 벡터 레이어에 설정 적용
        config.setIndividualLayerSettings(self.vector_layer, layer_settings)

        self.canvas.snappingUtils().setConfig(config)
        print("[DEBUG] Snapping configuration initialized")

    # 버텍스 편집 도구 초기화 함수 추가
    def initVertexTool(self):
        if self.vector_layer and self.vector_layer.isEditable():
            # 버텍스 편집 도구 생성
            self.vertex_tool = VertexEditTool(self.canvas, self.vector_layer)
            print("[DEBUG] 버텍스 편집 도구 초기화 완료")
            return True
        return False

    def initUI(self):
        self.setWindowTitle("QGIS Standalone Editor with Advanced Digitizing")
        self.setGeometry(100, 100, 1200, 800)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("파일")
        edit_menu = menubar.addMenu("편집")
        view_menu = menubar.addMenu("보기")

        load_action = QAction("벡터 레이어 열기", self)
        load_action.triggered.connect(self.loadVectorLayer)
        file_menu.addAction(load_action)

        self.action_start_edit = QAction("편집 시작", self)
        self.action_start_edit.triggered.connect(self.startEditing)
        edit_menu.addAction(self.action_start_edit)

        self.action_stop_edit = QAction("편집 종료", self)
        self.action_stop_edit.triggered.connect(self.stopEditing)
        edit_menu.addAction(self.action_stop_edit)

        self.action_add_feature = QAction("피처 추가", self)
        self.action_add_feature.triggered.connect(self.addFeature)
        edit_menu.addAction(self.action_add_feature)
        
        # 버텍스 편집 도구 메뉴 추가
        self.action_edit_vertex = QAction("버텍스 편집", self)
        self.action_edit_vertex.triggered.connect(self.activateVertexTool)
        edit_menu.addAction(self.action_edit_vertex)

        self.action_advanced_digitizing = QAction("고급 디지털화 도구", self)
        self.action_advanced_digitizing.triggered.connect(self.toggleAdvancedDigitizing)
        view_menu.addAction(self.action_advanced_digitizing)

        self.action_select = QAction("선택", self)
        self.action_select.triggered.connect(self.activateSelectTool)
        edit_menu.addAction(self.action_select)

    # 버텍스 편집 도구 활성화 함수 추가
    def activateVertexTool(self):
        if hasattr(self, "vector_layer") and self.vector_layer.isEditable():
            if self.initVertexTool():
                # 메인 스냅 인디케이터 숨기기
                self.snap_indicator.setVisible(False)
                
                # 버텍스 도구 활성화
                self.setMapTool(self.vertex_tool)
                QMessageBox.information(self, "버텍스 편집", "버텍스 편집 도구가 활성화되었습니다.\n버텍스를 드래그하여 편집하세요.")
            else:
                QMessageBox.warning(self, "경고", "버텍스 편집 도구를 초기화할 수 없습니다.")
        else:
            QMessageBox.warning(self, "경고", "먼저 편집 모드를 활성화하세요!")

    def initAdvancedDigitizing(self):
        self.adv_digi_dock = QgsAdvancedDigitizingDockWidget(self.canvas)
        self.addDockWidget(Qt.RightDockWidgetArea, self.adv_digi_dock)
        self.adv_digi_dock.setVisible(False)

    def toggleAdvancedDigitizing(self):
        self.adv_digi_dock.setVisible(not self.adv_digi_dock.isVisible())

    def loadVectorLayer(self):
        file_path = "test/ctprvn_20230729/ctprvn.shp"
        self.vector_layer = QgsVectorLayer(file_path, "편집 레이어", "ogr")
        self.project.addMapLayer(self.vector_layer)
        self.canvas.setLayers([self.vector_layer])
        self.canvas.zoomToFullExtent()

       # 스냅핑 대상 레이어 설정
        self.canvas.snappingUtils().setCurrentLayer(self.vector_layer)
        print("[DEBUG] Vector layer loaded and snapping layer set")

    def startEditing(self):
        if hasattr(self, "vector_layer"):
            self.vector_layer.startEditing()
            
            # 스냅 명시적 활성화
            config = self.canvas.snappingUtils().config()
            config.setEnabled(True)
            config.setTolerance(20)  # 테스트를 위해 큰 값으로 설정
            self.canvas.snappingUtils().setConfig(config)
            self.snap_indicator.setVisible(True)
            self.action_advanced_digitizing.setChecked(True)
            self.adv_digi_dock.setVisible(True)
            self.activateSelectTool()
            QMessageBox.information(self, "편집 시작", "편집 모드가 활성화되었습니다.")
        else:
            QMessageBox.warning(self, "경고", "먼저 벡터 레이어를 로드하세요!")

    def stopEditing(self):
        if hasattr(self, "vector_layer") and self.vector_layer.isEditable():
            self.vector_layer.commitChanges()
            # 스냅핑 비활성화
            config = self.canvas.snappingUtils().config()
            config.setEnabled(False)
            self.canvas.snappingUtils().setConfig(config)
            self.snap_indicator.setVisible(False)
            QMessageBox.information(self, "편집 종료", "변경 사항이 저장되었습니다.")
        else:
            QMessageBox.warning(self, "경고", "편집 모드가 아닙니다.")

    def addFeature(self):
        if hasattr(self, "vector_layer") and self.vector_layer.isEditable():
            self.canvas.setMapTool(QgsMapToolEdit(self.canvas))
            QMessageBox.information(self, "편집 도구", "새 피처 추가 모드 활성화")
        else:
            QMessageBox.warning(self, "경고", "편집 모드를 먼저 활성화하세요!")

    def activateSelectTool(self):
        self.setMapTool(self.select_tool)
        QMessageBox.information(self, "도구", "선택 도구가 활성화되었습니다.")

    def setMapTool(self, tool):
        self.canvas.unsetMapTool(self.canvas.mapTool())
        self.canvas.setMapTool(tool)

    def closeEvent(self, event):
        self.qgs.exitQgis()
        event.accept()

    def featureIdentified(self, feature):
        """ 피처가 선택되었을 때 호출되는 함수 """
        if feature:
            print("선택된 피처 ID:", feature.id())
            self.vector_layer.selectByIds([feature.id()])
            self.canvas.refresh()
            if self.vector_layer.isEditable():
                # 버텍스 편집 도구 초기화 및 활성화
                if self.initVertexTool():
                    self.setMapTool(self.vertex_tool)
                    print("[DEBUG] 버텍스 편집 도구 활성화")
                else:
                    self.setMapTool(self.edit_tool)
                
                # 스냅핑 활성화
                config = self.canvas.snappingUtils().config()
                config.setEnabled(True)
                self.canvas.snappingUtils().setConfig(config)
                self.snap_indicator.setVisible(True)
                
                # 고급 디지타이징 도구 활성화
                self.adv_digi_dock.setEnabled(True)
                for action in self.adv_digi_dock.findChildren(QAction):
                    action.setEnabled(True)
                # 또는 캔버스의 상태를 업데이트
                self.canvas.setFocus()
            else:
                QMessageBox.warning(self, "경고", "먼저 편집 모드를 활성화해야 버텍스를 편집할 수 있습니다.")
        else:
            print("선택된 피처 없음")

    def onMouseMove(self, point):
        """마우스가 움직일 때마다 스냅 표시기 업데이트"""
        # 스냅 결과 가져오기
        match = self.canvas.snappingUtils().snapToMap(point)
        if match.isValid():
            # 스냅 결과가 있으면 표시기 업데이트
            self.snap_indicator.setMatch(match)
            self.snap_indicator.setVisible(True)
            #print(f"[DEBUG] 스냅 발생: {match.point().x()}, {match.point().y()}")
        else:
            # 스냅 결과가 없으면 표시기 숨김
            self.snap_indicator.setVisible(False)