import sys
from PyQt5.QtWidgets import QApplication
from samples.LayerOrder import LayerOrder
from samples.LoadLayer import LoadLayer
from samples.AdvancedDigitizingWidget import AdvancedDigitizingWidget
from samples.EditToolBar import EditToolBar

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditToolBar()
    window.show()
    sys.exit(app.exec_())
