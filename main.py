import sys
from PyQt5.QtWidgets import QApplication
from samples.LayerOrder import LayerOrder
from samples.LoadLayer import LoadLayer
# from samples.Editor import Editor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LayerOrder()
    window.show()
    sys.exit(app.exec_())
