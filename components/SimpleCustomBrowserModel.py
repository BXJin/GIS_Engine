from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from qgis.gui import QgsBrowserGuiModel, QgsBrowserItem

class SimpleCustomBrowserModel(QgsBrowserGuiModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_item = QgsBrowserItem("My Custom Data", QgsBrowserItem.Root)
        self.item1 = QgsBrowserItem("Custom Item 1", QgsBrowserItem.File, self.root_item)
        self.item2 = QgsBrowserItem("Custom Group", QgsBrowserItem.Group, self.root_item)
        self.sub_item = QgsBrowserItem("Sub Item", QgsBrowserItem.File, self.item2)

        self.root_item.setChildren([self.item1, self.item2])
        self.item2.setChildren([self.sub_item])

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            if 0 <= row < len(self.root_item.children()):
                return self.createIndex(row, column, self.root_item.children()[row])
        elif parent.internalPointer() == self.root_item:
            if 0 <= row < len(self.item2.children()):
                return self.createIndex(row, column, self.item2.children()[row])
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        child_item = index.internalPointer()
        parent_item = child_item.parent()
        if parent_item == self.root_item:
            return QModelIndex()
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self.root_item.children())
        elif parent.internalPointer() == self.root_item:
            return len(self.item2.children())
        return 0

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.name()
        return None