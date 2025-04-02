"""
docstring
"""

from qgis.gui import QgsMapCanvas


class CanvasManager:
    """QgsMapCanvas 싱글톤 관리 클래스"""

    _instance = None  # 싱글톤 인스턴스 저장 변수

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CanvasManager, cls).__new__(cls)
            cls._instance.canvas = QgsMapCanvas()  # 맵 캔버스 생성
        return cls._instance

    @staticmethod
    def canvas():
        """싱글톤 `QgsMapCanvas` 반환"""
        return CanvasManager().canvas


def add(a: int, b: int):
    return a + b


add("bbb", 20, 111)
