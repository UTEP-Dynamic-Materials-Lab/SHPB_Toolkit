from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout
)
from rdflib import Graph, Namespace

class LaboratoryWidget(QWidget):
    def __init__(self, ontology_path, test_config):
        super().__init__()
        self.ontology_path = ontology_path
        self.test_config = test_config

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        # Laboratory Selection
        label = QLabel("Select Laboratory:")
        self.layout.addWidget(label)

        self.laboratory_combo = QComboBox()
        self.laboratory_combo.currentIndexChanged.connect(self.update_laboratory_details)
        self.layout.addWidget(self.laboratory_combo)

        # Add non-editable fields
        self.details_layout = QVBoxLayout()
        self.layout.addLayout(self.details_layout)

        self.populate_laboratories()

    def populate_laboratories(self):
        """Populate the combo box with laboratory instances."""
        query = """
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?labInstance ?labName WHERE {
            ?labInstance rdf:type :Laboratory ;
                         :hasName ?labName .
        }
        """
        try:
            results = self.ontology.query(query)

            for row in results:
                lab_name = str(row.labName)
                lab_instance = str(row.labInstance)
                self.laboratory_combo.addItem(lab_name, lab_instance)

            # Auto-select the first item if available
            if self.laboratory_combo.count() > 0:
                self.update_laboratory_details()

        except Exception as e:
            print(f"Error querying laboratories: {e}")

    def update_laboratory_details(self):
        """Update the displayed details based on the selected laboratory."""
        # Clear previous details
        while self.details_layout.count():
            item = self.details_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get selected laboratory instance
        lab_instance = self.laboratory_combo.currentData()
        if not lab_instance:
            return

        # Query details for the selected laboratory
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?affiliation ?location ?supervisor WHERE {{
            <{lab_instance}> :hasAffiliation ?affiliation ;
                             :hasLocation ?location ;
                             :hasSupervisor ?supervisor .
        }}
        """
        try:
            results = self.ontology.query(query)
            for row in results:
                # Display details as non-editable fields
                self.details_layout.addWidget(QLabel(f"Affiliation: {row.affiliation}"))
                self.details_layout.addWidget(QLabel(f"Location: {row.location}"))
                self.details_layout.addWidget(QLabel(f"Supervisor: {row.supervisor}"))

        except Exception as e:
            print(f"Error querying details for laboratory {lab_instance}: {e}")
