
canvas = iface.mapCanvas()
digitizing = QgsAdvancedDigitizingDockWidget(canvas)
digitizing.show()



main_window = iface.mainWindow()
edit_toolbar = main_window.findChild(QToolBar, 'mEditingToolBar')
edit_toolbar.setVisible(True)  # 편집 툴바 표시