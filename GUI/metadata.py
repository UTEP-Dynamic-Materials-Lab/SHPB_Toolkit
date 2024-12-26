from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QComboBox, QPushButton, QFileDialog, QMessageBox
)
from rdflib import Graph

class AddExperimentWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Experiment")
        self.resize(400, 300)

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse("ontology.ttl", format="turtle")

        # Layout and widgets
        layout = QVBoxLayout()

        # Test Name
        layout.addWidget(QLabel("Test Name:"))
        self.test_name_input = QLineEdit()
        layout.addWidget(self.test_name_input)

        # Material dropdown
        layout.addWidget(QLabel("Material:"))
        self.material_dropdown = QComboBox()
        self.populate_dropdown(self.material_dropdown, ":Material")
        layout.addWidget(self.material_dropdown)

        # Test Type dropdown
        layout.addWidget(QLabel("Test Type:"))
        self.test_type_dropdown = QComboBox()
        self.populate_dropdown(self.test_type_dropdown, ":TestType")
        layout.addWidget(self.test_type_dropdown)

        # File Upload
        layout.addWidget(QLabel("Upload Raw Data:"))
        self.upload_button = QPushButton("Select File")
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button)
        self.file_path_label = QLabel("No file selected")
        layout.addWidget(self.file_path_label)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_experiment)
        layout.addWidget(self.submit_button)

        # Back button
        self.back_button = QPushButton("Back to Main")
        self.back_button.clicked.connect(self.close)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def populate_dropdown(self, dropdown, ontology_class):
        query = f"""
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?individual ?label WHERE {{
            ?individual rdf:type {ontology_class} .
            ?individual :hasName ?label .
        }}
        """
        results = self.ontology.query(query)
        for individual, label in results:
            dropdown.addItem(label, individual)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Raw Data File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.file_path_label.setText(file_path)

    def submit_experiment(self):
        test_name = self.test_name_input.text()
        material = self.material_dropdown.currentData()
        test_type = self.test_type_dropdown.currentData()
        file_path = self.file_path_label.text()

        if not test_name or not material or not test_type or file_path == "No file selected":
            QMessageBox.warning(self, "Missing Information", "Please fill all fields and select a file.")
            return

        # Placeholder: Save metadata and raw data to TTL file
        QMessageBox.information(self, "Success", "Experiment added successfully!")
