from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QComboBox, QDoubleSpinBox, QHBoxLayout, QWidget, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt
from rdflib import Graph, Namespace

class FEAMetadataWindow(QMainWindow):
    def __init__(self, ontology_path, test_config, bar_instance):
        super().__init__()
        self.setWindowTitle(f"FEA Metadata for {bar_instance}")
        self.setGeometry(100, 100, 600, 450)
        self.ontology_path = ontology_path
        self.test_config = test_config
        self.bar_instance = bar_instance

        # Load Ontology
        self.ontology = Graph()
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
            
        # Model Selection
        model_label = QLabel("Select Strength Model:")
        self.layout.addWidget(model_label)
    
        self.model_combo = QComboBox()
        self.populate_strength_models()
        self.model_combo.currentIndexChanged.connect(self.populate_parameters)
        self.layout.addWidget(self.model_combo)
    
        # Parameter Fields Section
        parameter_section_label = QLabel("Parameters:")
        self.layout.addWidget(parameter_section_label)
    
        # Initialize parameter layout
        self.parameter_layout = QVBoxLayout()  # Dedicated layout for parameters
        parameter_scroll_area = QScrollArea()
        parameter_scroll_area.setWidgetResizable(True)
    
        # Create a widget to hold the parameter layout
        parameter_widget = QWidget()
        parameter_widget.setLayout(self.parameter_layout)
        parameter_scroll_area.setWidget(parameter_widget)
    
        self.layout.addWidget(parameter_scroll_area)
    
        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        self.layout.addWidget(close_button)

    def populate_strength_models(self):
        """Populate the strength models available."""
        query = """
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?modelInstance ?modelName WHERE {
            ?modelInstance rdf:type :StrengthModel ;
                           :hasName ?modelName .
        }
        """
        results = self.ontology.query(query)
        for row in results:
            model_name = str(row.modelName)
            model_instance = str(row.modelInstance)
            self.model_combo.addItem(model_name, model_instance)

    def populate_parameters(self):
        """Populate parameter fields for the selected strength model."""
        # Clear existing parameter fields
        while self.parameter_layout.count():
            item = self.parameter_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
            if layout := item.layout():
                while layout.count():
                    sub_item = layout.takeAt(0)
                    if sub_widget := sub_item.widget():
                        sub_widget.deleteLater()
                    if sub_layout := sub_item.layout():
                        sub_layout.deleteLater()
        
        # Get the selected model instance
        model_instance = self.model_combo.currentData()
        
        if model_instance:
            query = f"""
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT ?parameter ?paramName ?unitAbbreviation WHERE {{
                <{model_instance}> :hasParameter ?parameter .
                ?parameter :hasName ?paramName ;
                           :hasUnits ?unit .
                ?unit :hasAbbreviation ?unitAbbreviation .
            }}
            """
            results = self.ontology.query(query)
        
            # Dictionary to store parameter info and units
            parameter_info = {}
        
            for row in results:
                param_name = str(row.paramName)
                unit_abbreviation = str(row.unitAbbreviation)
        
                if param_name not in parameter_info:
                    parameter_info[param_name] = {"units": []}
                parameter_info[param_name]["units"].append(unit_abbreviation)
        
            # Create fields for each parameter
            for param_name, data in parameter_info.items():
                # Parameter label
                param_label = QLabel(f"{param_name}:")
        
                # Spinbox for value input
                spinbox = QDoubleSpinBox()
                spinbox.setRange(0.0, 1e6)
                spinbox.setDecimals(4)
        
                # Unit selector (QComboBox)
                unit_combo = QComboBox()
                unit_combo.addItems(data["units"])
        
                # Add parameter layout
                param_layout = QHBoxLayout()
                param_layout.addWidget(param_label)
                param_layout.addWidget(spinbox)
                param_layout.addWidget(unit_combo)
        
                self.parameter_layout.addLayout(param_layout)
        else:
            # If no model is selected, print a message
            print("No model instance selected. Parameter fields cleared.")

