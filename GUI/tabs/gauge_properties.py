from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QDoubleSpinBox, QComboBox, QHBoxLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from rdflib import Graph, Namespace

class GaugePropertiesWidget(QWidget):
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
        """Initialize UI components."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_area_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_area_widget.setLayout(scroll_layout)

        self.populate_fields(scroll_layout)

        scroll_area.setWidget(scroll_area_widget)
        self.layout.addWidget(scroll_area)

    def populate_fields(self, layout):
        """Populate input fields based on StrainGaugeProperties instances."""
        query = """
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?property ?name ?unitAbbreviation WHERE {
            ?property rdf:type :StrainGaugeProperties ;
                      :hasName ?name ;
                      :hasUnits ?unit .
            ?unit :hasAbbreviation ?unitAbbreviation .
        }
        """
        results = self.ontology.query(query)

        # Track properties to prevent duplicates
        property_info = {}

        for row in results:
            name = str(row.name)
            unit_abbreviation = str(row.unitAbbreviation)

            if name not in property_info:
                property_info[name] = {"units": []}
            property_info[name]["units"].append(unit_abbreviation)

        # Create input fields for each property
        for name, data in property_info.items():
            label = QLabel(f"{name}:")
            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.0, 1e6)
            spinbox.setDecimals(4)

            unit_combo = QComboBox()
            unit_combo.addItems(data["units"])  # Populate all units for the property

            # Layout for each property
            field_layout = QHBoxLayout()
            field_layout.addWidget(label)
            field_layout.addWidget(spinbox)
            field_layout.addWidget(unit_combo)

            layout.addLayout(field_layout)
