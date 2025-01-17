from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
from GUI.add_experiment import AddExperimentWindow
from config.test_config import TestConfiguration
import sys

class MainWindow(QMainWindow):
    def __init__(self, ontology_path, test_config):
        super().__init__()
        self.setWindowTitle("SHPB Toolkit")
        self.setGeometry(100, 100, 400, 200)

        self.test_config = test_config

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        self.add_experiment_button = QPushButton("Add Experiment")
        self.add_experiment_button.clicked.connect(lambda: self.add_experiment(ontology_path))
        self.layout.addWidget(self.add_experiment_button)

        self.central_widget.setLayout(self.layout)

    def add_experiment(self, ontology_path):
        self.add_exp_window = AddExperimentWindow(ontology_path, self.test_config)
        self.add_exp_window.show()

if __name__ == "__main__":
    ontology_path = "ontology/DynaMat_SHPB.ttl"
    test_config = TestConfiguration()
    app = QApplication(sys.argv)
    main_window = MainWindow(ontology_path, test_config)
    main_window.show()
    sys.exit(app.exec())
