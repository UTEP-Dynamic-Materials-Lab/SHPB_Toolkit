from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QPushButton, QScrollArea
)
from rdflib import Graph, Namespace, URIRef
from GUI.components.common_widgets import MaterialSelector, ClassInstanceSelection, SetDefaults

class LaboratoryWidget(QWidget):
    def __init__(self, ontology_path, test_config, experiment_temp_file):
        super().__init__()
        self.ontology_path = ontology_path
        self.test_config = test_config
        self.experiment = experiment_temp_file
        self.test_name = self.test_config.test_name
        self.lab_properties = {}

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Create a main layout for this widget
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)  
        
        # Initialize UI elements
        self.init_ui()
        self.layout.addStretch()

    def init_ui(self):
        """Initialize the UI components."""
        # Laboratory Selection
        label = QLabel("Select Laboratory:")
        self.layout.addWidget(label)

        self.laboratory_combo = ClassInstanceSelection(self.ontology_path, self.experiment.DYNAMAT.Laboratory)
        self.laboratory_combo.currentIndexChanged.connect(self.update_laboratory_details)
        self.layout.addWidget(self.laboratory_combo)

        # Add non-editable fields
        self.details_layout = QVBoxLayout()
        self.update_laboratory_details()
        self.layout.addLayout(self.details_layout)

        # Confirm/Edit Button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.toggle_confirm_edit)
        self.layout.addWidget(self.confirm_button)  

    def update_laboratory_details(self):
        """Update the displayed details based on the selected laboratory."""
        # Clear previous details
        while self.details_layout.count():
            item = self.details_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get selected laboratory instance
        lab_instance, _ = self.laboratory_combo.currentData()

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
                self.lab_properites = {
                    "Affiliation" : row.affiliation,
                    "Location" : row.location, 
                    "Supervisor": row.supervisor
                }
                

        except Exception as e:
            print(f"Error querying details for laboratory {lab_instance}: {e}")

    def toggle_confirm_edit(self):
        """Toggle between Confirm and Edit modes."""
        editable = self.confirm_button.text() == "Edit"
        self.laboratory_combo.setEnabled(editable)
        self.confirm_button.setText("Confirm" if editable else "Edit")

        # Add data to temp file
        if not editable:
            metadata_uri = self.experiment.DYNAMAT["Experiment_Metadata"]
            laboratory_uri , _ = self.laboratory_combo.currentData()
            
            # Add Metadata Triples
            self.experiment.set_triple(str(laboratory_uri), str(self.experiment.RDF.type),
                                       str(self.experiment.DYNAMAT.Laboratory)) 
            self.experiment.add_instance_data(laboratory_uri)
            self.experiment.set_triple(str(metadata_uri), str(self.experiment.DYNAMAT.hasLaboratory),
                                       str(laboratory_uri))  
            self.experiment.save()   

    def update_test_name(self, test_name):
        """ Updates the current test name"""
        self.test_name = test_name
