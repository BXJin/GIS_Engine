import sys
from PyQt5.QtWidgets import QApplication
from samples.LayerOrder import LayerOrder
from samples.LoadLayer import LoadLayer
from samples.AdvancedDigitizingWidget import AdvancedDigitizingWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedDigitizingWidget()
    window.show()
    sys.exit(app.exec_())
