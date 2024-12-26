from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QMessageBox
)
from PyQt6.QtCore import QDate
import sys
from rdflib import Graph

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SHPB Toolkit")

        self.layout = QVBoxLayout()

        # Add Experiment Button
        self.add_experiment_button = QPushButton("Add Experiment")
        self.add_experiment_button.clicked.connect(self.add_experiment)
        self.layout.addWidget(self.add_experiment_button)

        # Visualize Experiments Button
        self.visualize_experiments_button = QPushButton("Visualize Experiments")
        self.visualize_experiments_button.clicked.connect(self.visualize_experiments)
        self.layout.addWidget(self.visualize_experiments_button)

        # Set central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def add_experiment(self):
        self.add_exp_window = AddExperimentWindow()
        self.add_exp_window.show()

    def visualize_experiments(self):
        self.vis_exp_window = VisualizeExperimentsWindow()
        self.vis_exp_window.show()

class AddExperimentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Experiment Metadata")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout()

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse("ontology/DynaMat_SHPB.ttl", format="turtle")

        # Test Name Input
        self.test_name_label = QLabel("Test Name (e.g., 001_2024-12-23_316SS_LAB_RT_001):")
        self.test_name_input = QLineEdit()
        self.test_name_input.setPlaceholderText("Enter a descriptive test name")
        self.layout.addWidget(self.test_name_label)
        self.layout.addWidget(self.test_name_input)

        # Test Date Input
        self.test_date_label = QLabel("Test Date:")
        self.test_date_input = QDateEdit()
        self.test_date_input.setCalendarPopup(True)
        self.test_date_input.setDate(QDate.currentDate())
        self.layout.addWidget(self.test_date_label)
        self.layout.addWidget(self.test_date_input)

        # User Input
        self.user_label = QLabel("User:")
        self.user_input = QComboBox()
        self.populate_user_dropdown()
        self.layout.addWidget(self.user_label)
        self.layout.addWidget(self.user_input)

        # Data Acquisition Rate
        self.daq_rate_label = QLabel("Data Acquisition Rate (Hz):")
        self.daq_rate_input = QComboBox()
        self.daq_rate_input.addItems(["10 kHz", "20 kHz", "50 kHz", "100 kHz"])
        self.layout.addWidget(self.daq_rate_label)
        self.layout.addWidget(self.daq_rate_input)

        # Submit Button
        self.submit_button = QPushButton("Next")
        self.submit_button.clicked.connect(self.collect_metadata)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

    def populate_user_dropdown(self):
        query = """
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?userAbbreviation
        WHERE {
            ?user a :User ;
                  :hasAbbreviation ?userAbbreviation .
        }
        """
        results = self.ontology.query(query)
        for row in results:
            self.user_input.addItem(str(row[0]))

    def collect_metadata(self):
        test_name = self.test_name_input.text()
        test_date = self.test_date_input.date().toString("yyyy-MM-dd")
        user = self.user_input.currentText()
        daq_rate = self.daq_rate_input.currentText()

        # Validate inputs
        if not test_name or not user:
            QMessageBox.warning(self, "Input Error", "Please fill out all required fields.")
            return

        # Log metadata (for now, print to console)
        print(f"Test Name: {test_name}")
        print(f"Test Date: {test_date}")
        print(f"User: {user}")
        print(f"Data Acquisition Rate: {daq_rate}")

        QMessageBox.information(self, "Success", "Metadata collected successfully.")
        self.close()

class VisualizeExperimentsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualize Experiments")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()
        self.label = QLabel("Visualize Experiments Placeholder")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load ontology (optional setup for future integrations)
    ontology = Graph()
    ontology.parse("ontology/DynaMat_SHPB.ttl", format="turtle")

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
