from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QMessageBox, QTabWidget, QSpinBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import QDate
import sys
from rdflib import Graph, Namespace

class AddExperimentWindow(QWidget):
    def __init__(self, ontology_path):
        super().__init__()
        self.setWindowTitle("Add Experiment Metadata")
        self.setGeometry(100, 100, 500, 400)

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        self.namespace = Namespace("http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#")

        # Main Layout with Tabs
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.init_landing_page()

        self.setLayout(self.layout)

    def init_landing_page(self):
        # Landing Page Layout
        landing_page = QWidget()
        layout = QVBoxLayout()

        # Test Name (Non-editable)
        self.test_name_label = QLabel("Generated Test Name:")
        self.test_name_display = QLineEdit()
        self.test_name_display.setReadOnly(True)
        layout.addWidget(self.test_name_label)
        layout.addWidget(self.test_name_display)

        # User Selection
        user_label = QLabel("User:")
        self.user_combo = QComboBox()
        self.populate_users()
        self.user_combo.currentIndexChanged.connect(self.update_test_name)
        layout.addWidget(user_label)
        layout.addWidget(self.user_combo)

        # Date Input
        date_label = QLabel("Test Date:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.dateChanged.connect(self.update_test_name)
        layout.addWidget(date_label)
        layout.addWidget(self.date_input)

        # Material Selection
        material_label = QLabel("Material:")
        self.material_combo = QComboBox()
        self.populate_materials()
        self.material_combo.currentIndexChanged.connect(self.update_test_name)
        layout.addWidget(material_label)
        layout.addWidget(self.material_combo)

        # LAB/FEA Toggle
        lab_fea_label = QLabel("Test Type:")
        self.lab_radio = QRadioButton("LAB")
        self.fea_radio = QRadioButton("FEA")
        self.lab_fea_group = QButtonGroup()
        self.lab_fea_group.addButton(self.lab_radio)
        self.lab_fea_group.addButton(self.fea_radio)
        self.lab_radio.setChecked(True)
        self.lab_radio.toggled.connect(self.update_test_name)
        lab_fea_layout = QHBoxLayout()
        lab_fea_layout.addWidget(self.lab_radio)
        lab_fea_layout.addWidget(self.fea_radio)
        layout.addWidget(lab_fea_label)
        layout.addLayout(lab_fea_layout)

        # HT/RT Toggle
        ht_rt_label = QLabel("Environment:")
        self.ht_radio = QRadioButton("HT")
        self.rt_radio = QRadioButton("RT")
        self.ht_rt_group = QButtonGroup()
        self.ht_rt_group.addButton(self.ht_radio)
        self.ht_rt_group.addButton(self.rt_radio)
        self.rt_radio.setChecked(True)
        self.ht_radio.toggled.connect(self.update_test_name)
        ht_rt_layout = QHBoxLayout()
        ht_rt_layout.addWidget(self.ht_radio)
        ht_rt_layout.addWidget(self.rt_radio)
        layout.addWidget(ht_rt_label)
        layout.addLayout(ht_rt_layout)

        # Experiment ID
        exp_id_label = QLabel("Experiment ID:")
        self.exp_id_spinbox = QSpinBox()
        self.exp_id_spinbox.setRange(1, 999)
        self.exp_id_spinbox.setValue(1)
        self.exp_id_spinbox.valueChanged.connect(self.update_test_name)
        layout.addWidget(exp_id_label)
        layout.addWidget(self.exp_id_spinbox)

        landing_page.setLayout(layout)
        self.tabs.addTab(landing_page, "Landing Page")

    def populate_users(self):
        query = """
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?user ?fullName ?abbreviation WHERE {
            ?user a :User ;
                  :hasFullName ?fullName ;
                  :hasAbbreviation ?abbreviation .
        }
        """
        for row in self.ontology.query(query):
            self.user_combo.addItem(f"{row.fullName} ({row.abbreviation})", row.abbreviation)

    def populate_materials(self):
        query = """
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?materialName ?abbreviation WHERE {
            ?material a :Material ;
                      :hasLegendName ?materialName ;
                      :hasAbbreviation ?abbreviation .
        }
        """
        self.material_combo.clear()  # Clear any existing items
        for row in self.ontology.query(query):
            material_name = str(row.materialName)
            abbreviation = str(row.abbreviation)
            self.material_combo.addItem(f"{material_name} ({abbreviation})", abbreviation)



    def update_test_name(self):
        user_abbreviation = self.user_combo.currentData()
        date = self.date_input.date().toString("yyyyMMdd")
        material_abbreviation = self.material_combo.currentData()
        lab_fea = "LAB" if self.lab_radio.isChecked() else "FEA"
        ht_rt = "HT" if self.ht_radio.isChecked() else "RT"
        experiment_id = f"{self.exp_id_spinbox.value():03}"

        if user_abbreviation and material_abbreviation:
            test_name = f"{user_abbreviation}_{date}_{material_abbreviation}_{lab_fea}_{ht_rt}_{experiment_id}"
            self.test_name_display.setText(test_name)

class MainWindow(QMainWindow):
    def __init__(self, ontology_path):
        super().__init__()
        self.setWindowTitle("SHPB Toolkit")
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        self.add_experiment_button = QPushButton("Add Experiment")
        self.add_experiment_button.clicked.connect(lambda: self.add_experiment(ontology_path))
        self.layout.addWidget(self.add_experiment_button)

        self.central_widget.setLayout(self.layout)

    def add_experiment(self, ontology_path):
        self.add_exp_window = AddExperimentWindow(ontology_path)
        self.add_exp_window.show()

if __name__ == "__main__":
    ontology_path = "ontology/DynaMat_SHPB.ttl"
    app = QApplication(sys.argv)
    main_window = MainWindow(ontology_path)
    main_window.show()
    sys.exit(app.exec())
