from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from qgis.core import QgsGeometry, QgsPointXY, QgsWkbTypes
from qgis.gui import QgsMapToolEdit, QgsSnapIndicator, QgsRubberBand

class VertexEditTool(QgsMapToolEdit):
    def __init__(self, canvas, layer):
        super().__init__(canvas)
        self.canvas = canvas
        self.layer = layer
        self.dragging = False
        self.selected_feature = None
        self.selected_vertex = None
        self.vertex_index = -1
        self.snap_indicator = QgsSnapIndicator(canvas)
        self.rubber_band = QgsRubberBand(canvas)
        self.rubber_band.setColor(QColor(255, 0, 0, 100))
        self.rubber_band.setWidth(2)
    
    def canvasMoveEvent(self, event):
        if not self.dragging:
            # 마우스 이동 시 스냅 인디케이터 업데이트
            match = self.canvas.snappingUtils().snapToMap(event.pos())
            if match.isValid():
                self.snap_indicator.setMatch(match)
                self.snap_indicator.setVisible(True)
            else:
                self.snap_indicator.setVisible(False)
        else:
            # 버텍스를 드래그 중일 때
            if self.selected_feature and self.vertex_index >= 0:
                # 현재 위치에 스냅
                match = self.canvas.snappingUtils().snapToMap(event.pos())
                if match.isValid():
                    point = match.point()
                else:
                    point = self.toMapCoordinates(event.pos())
                
                # 임시 geometry 생성 및 표시
                geom = self.selected_feature.geometry()
                if geom.type() == QgsWkbTypes.PolygonGeometry:
                    # 폴리곤의 경우 임시로 geometry 복사하여 표시
                    new_geom = QgsGeometry(geom)
                    new_geom.moveVertex(point.x(), point.y(), self.vertex_index)
                    self.rubber_band.setToGeometry(new_geom, self.layer)
                
                # 스냅 인디케이터 업데이트
                self.snap_indicator.setMatch(match)
                self.snap_indicator.setVisible(match.isValid())
    
    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 선택된 피처가 있는지 확인
            features = self.layer.selectedFeatures()
            if not features:
                return
            
            # 첫 번째 선택된 피처 사용
            self.selected_feature = features[0]
            
            # 클릭한 위치에서 가장 가까운 버텍스 찾기
            geom = self.selected_feature.geometry()
            click_point = self.toMapCoordinates(event.pos())
            
            closest_vertex = None
            min_distance = float('inf')
            vertex_index = -1
            
            # 모든 버텍스 순회
            vertex_id = 0
            for vertex in geom.vertices():
                vertex_point = QgsPointXY(vertex.x(), vertex.y())
                distance = click_point.distance(vertex_point)
                if distance < min_distance:
                    min_distance = distance
                    closest_vertex = vertex_point
                    vertex_index = vertex_id
                vertex_id += 1
            
            # 충분히 가까운 버텍스를 클릭했는지 확인
            tolerance = self.canvas.mapSettings().mapUnitsPerPixel() * 10
            if min_distance <= tolerance:
                self.dragging = True
                self.selected_vertex = closest_vertex
                self.vertex_index = vertex_index
                
                # 러버밴드 초기화
                self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
                self.rubber_band.addGeometry(geom, self.layer)
                
                print(f"[DEBUG] 버텍스 선택됨: 인덱스 {vertex_index}, 좌표 {closest_vertex.x()}, {closest_vertex.y()}")
    
    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            
            # 선택된 피처와 버텍스가 있는지 확인
            if self.selected_feature and self.vertex_index >= 0:
                # 현재 위치에 스냅
                match = self.canvas.snappingUtils().snapToMap(event.pos())
                if match.isValid():
                    point = match.point()
                else:
                    point = self.toMapCoordinates(event.pos())
                
                # 실제 지오메트리 업데이트
                geom = self.selected_feature.geometry()
                
                # 버텍스 수정
                if geom.moveVertex(point.x(), point.y(), self.vertex_index):
                    self.layer.changeGeometry(self.selected_feature.id(), geom)
                    self.canvas.refresh()
                    print(f"[DEBUG] 버텍스 이동됨: 새 좌표 {point.x()}, {point.y()}")
                else:
                    print("[DEBUG] 버텍스 이동 실패")
                
                # 러버밴드 초기화
                self.rubber_band.reset() 