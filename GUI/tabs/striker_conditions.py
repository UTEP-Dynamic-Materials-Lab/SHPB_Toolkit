from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QDoubleSpinBox, QComboBox, QRadioButton, QButtonGroup
)
from rdflib import Graph, Namespace
from PyQt6.QtCore import pyqtSignal

class StrikerConditionsWidget(QWidget):
    def __init__(self, ontology_path, test_config):
        super().__init__()
        self.test_config = test_config
        self.ontology_path = ontology_path

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#")

        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""

        # Striker Velocity
        striker_velocity_label = QLabel("Striker Velocity:")
        striker_velocity_layout = QHBoxLayout()
        self.striker_velocity_spinbox = QDoubleSpinBox()
        self.striker_velocity_spinbox.setRange(0.0, 1000.0)
        self.striker_velocity_spinbox.setDecimals(2)
        self.striker_velocity_unit_combo = QComboBox()
        self.populate_units("Velocity", self.striker_velocity_unit_combo)
        striker_velocity_layout.addWidget(self.striker_velocity_spinbox)
        striker_velocity_layout.addWidget(self.striker_velocity_unit_combo)
        self.layout.addWidget(striker_velocity_label)
        self.layout.addLayout(striker_velocity_layout)

        # Striker Pressure
        striker_pressure_label = QLabel("Striker Pressure:")
        striker_pressure_layout = QHBoxLayout()
        self.striker_pressure_spinbox = QDoubleSpinBox()
        self.striker_pressure_spinbox.setRange(0.0, 10000.0)
        self.striker_pressure_spinbox.setDecimals(2)
        self.striker_pressure_unit_combo = QComboBox()
        self.populate_units("Pressure", self.striker_pressure_unit_combo)
        striker_pressure_layout.addWidget(self.striker_pressure_spinbox)
        striker_pressure_layout.addWidget(self.striker_pressure_unit_combo)
        self.layout.addWidget(striker_pressure_label)
        self.layout.addLayout(striker_pressure_layout)

        # Momentum Trap State
        momentum_trap_label = QLabel("Momentum Trap State:")
        self.momentum_engaged_radio = QRadioButton("Engaged")
        self.momentum_not_engaged_radio = QRadioButton("Not Engaged")
        self.momentum_group = QButtonGroup()
        self.momentum_group.addButton(self.momentum_engaged_radio)
        self.momentum_group.addButton(self.momentum_not_engaged_radio)
        self.momentum_not_engaged_radio.setChecked(True)
        momentum_trap_layout = QHBoxLayout()
        momentum_trap_layout.addWidget(self.momentum_engaged_radio)
        momentum_trap_layout.addWidget(self.momentum_not_engaged_radio)
        self.layout.addWidget(momentum_trap_label)
        self.layout.addLayout(momentum_trap_layout)

    def populate_units(self, dimension, combo_box):
        """Populate units for a given dimension."""
        query = f"""
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT DISTINCT ?unitAbbreviation WHERE {{
            :{dimension} rdf:type :Dimension ;
                         :hasUnits ?unit .
            ?unit :hasAbbreviation ?unitAbbreviation .
        }}
        """
        try:
            results = self.ontology.query(query)
    
            if results:
                combo_box.clear()  # Clear existing items
                for row in results:
                    # Add plain text for PyQt compatibility
                    unit_symbol = str(row.unitAbbreviation)
                    combo_box.addItem(unit_symbol)
            else:
                print(f"No units found for dimension: {dimension}")
        except Exception as e:
            print(f"Error querying units for dimension {dimension}: {e}")



