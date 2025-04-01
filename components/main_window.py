from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QHBoxLayout, QStackedWidget)
from samples.LayerOrder import LayerOrder
from samples.LoadLayer import LoadLayer
from samples.AdvancedDigitizingWidget import AdvancedDigitizingWidget
from samples.EditToolBar import EditToolBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GIS Engine Demo")
        self.setGeometry(100, 100, 1200, 800)

        # 메인 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 전체 레이아웃
        main_layout = QHBoxLayout(main_widget)
        
        # 왼쪽 사이드바 (버튼들)
        sidebar = QWidget()
        sidebar.setMaximumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # 버튼 생성
        btn_layer_order = QPushButton("레이어 순서 관리", self)
        btn_layer_order.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        sidebar_layout.addWidget(btn_layer_order)

        btn_load_layer = QPushButton("레이어 로드", self)
        btn_load_layer.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        sidebar_layout.addWidget(btn_load_layer)

        btn_digitizing = QPushButton("고급 디지타이징", self)
        btn_digitizing.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        sidebar_layout.addWidget(btn_digitizing)
        
        btn_edit_toolbar = QPushButton("편집 도구", self)  # EditToolbar 버튼 추가
        btn_edit_toolbar.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        sidebar_layout.addWidget(btn_edit_toolbar)

        # 나머지 공간을 채우는 빈 위젯 추가
        spacer = QWidget()
        sidebar_layout.addWidget(spacer)
        sidebar_layout.setStretchFactor(spacer, 1)
        
        # 스택 위젯 설정 (메인 컨텐츠 영역)
        self.stacked_widget = QStackedWidget()
        
        # 각 페이지 생성 및 추가
        self.layer_order = LayerOrder()
        self.load_layer = LoadLayer()
        self.digitizing = AdvancedDigitizingWidget()
        self.edit_toolbar = EditToolBar()
        
        self.stacked_widget.addWidget(self.layer_order)
        self.stacked_widget.addWidget(self.load_layer)
        self.stacked_widget.addWidget(self.digitizing)
        self.stacked_widget.addWidget(self.edit_toolbar)  
        
        # 레이아웃에 위젯 추가
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)
        
        # 기본 페이지 설정
        self.stacked_widget.setCurrentIndex(2) 