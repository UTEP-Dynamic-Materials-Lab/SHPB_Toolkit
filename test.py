from PyQt6.QtWidgets import QApplication, QListWidget, QVBoxLayout, QPushButton, QWidget
from PyQt6.QtCore import Qt

class MultiSelectExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multiple Selection Example")
        self.setGeometry(100, 100, 300, 200)

        # Create layout
        self.layout = QVBoxLayout(self)

        # Create QListWidget with multiple selection enabled
        self.list_widget = QListWidget()
        self.list_widget.addItems(["Test 1", "Test 2", "Test 3", "Test 4", "Test 5"])
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        # Add a button to fetch selected items
        self.get_selected_button = QPushButton("Get Selected Items")
        self.get_selected_button.clicked.connect(self.get_selected_items)

        # Add widgets to layout
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.get_selected_button)

    def get_selected_items(self):
        # Fetch selected items
        selected_items = self.list_widget.selectedItems()
        selected_texts = [item.text() for item in selected_items]
        print("Selected Items:", selected_texts)


if __name__ == "__main__":
    app = QApplication([])
    window = MultiSelectExample()
    window.show()
    app.exec()
