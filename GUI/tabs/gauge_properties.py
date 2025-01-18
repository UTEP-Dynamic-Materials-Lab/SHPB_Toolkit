from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QDoubleSpinBox, QComboBox, QHBoxLayout, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt
from rdflib import Graph, Namespace, URIRef
from GUI.components.common_widgets import ClassInstanceSelection, UnitSelector, DoubleSpinBox, SetDefaults
from config.strain_gauge_config import SGConfiguration

class GaugePropertiesWidget(QWidget):
    def __init__(self, ontology_path, experiment_temp_file):
        super().__init__()
        self.ontology_path = ontology_path        
        self.experiment = experiment_temp_file
        self.sg_config = SGConfiguration()
        self.property_info = {} # Tracks Gauge Properties
        

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)       

        self.init_ui()

        # Confirm/Edit Button
        self.confirm_button = QPushButton("Confirm SG Properties")
        self.confirm_button.clicked.connect(self.toggle_confirm_edit)
        self.layout.addWidget(self.confirm_button) 
        self.layout.addStretch()

    #################################################
    ## MAIN WIDGET WINDOW
    #################################################

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

    #################################################
    ## POPULATE FIELDS
    #################################################

    def populate_fields(self, layout):
        """Populate input fields based on StrainGaugeProperties instances."""
        query = """
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?property ?name WHERE {
            ?property rdf:type :StrainGaugeProperties ;
                      :hasName ?name .
        }
        """
        results = self.ontology.query(query)

        for row in results:
            property_uri = str(row.property)
            name = str(row.name)

            label = QLabel(f"{name}:")
            
            spinbox = DoubleSpinBox()
            unit_combo = UnitSelector(self.ontology_path, property_uri)

            try: 
                spinbox.setValue(float(self.sg_config[f"{property_uri.split('#')[-1]}_value"]))
                SetDefaults(self.ontology_path, 
                            self.sg_config[f"{property_uri.split('#')[-1]}_units"],
                            unit_combo)
            except:
                print(f"Default values not found for: {property_uri.split('#')[-1]}")

            # Layout for each property
            field_layout = QHBoxLayout()
            field_layout.addWidget(label)
            field_layout.addWidget(spinbox)
            field_layout.addWidget(unit_combo)

            layout.addLayout(field_layout)
            
            # Store widget references in property_info
            if property_uri not in self.property_info:
                self.property_info[property_uri] = []

            self.property_info[property_uri].append({
                "spinbox": spinbox,
                "combo_box": unit_combo
                })

    #################################################
    ## ADD DATA FIELDS TO RDF
    #################################################
    def toggle_confirm_edit(self):
        """Toggle between Confirm and Edit modes."""
        
        editable = self.confirm_button.text() == "Edit SG Properties"

        for property_type_uri in self.property_info:
            for prop in self.property_info[property_type_uri]:
                # Set spinbox and combo box editable or non-editable
                try:
                    prop["spinbox"].setEnabled(editable)
                    prop["combo_box"].setEnabled(editable)                    
                except: 
                    continue
        # Update the button text
        self.confirm_button.setText("Confirm SG Properties" if editable else "Edit SG Properties")

        if not editable:
            testing_conditions_uri = self.experiment.DYNAMAT["Testing_Conditions"]
            
            for property_type_uri, properties in self.property_info.items():
                
                for prop in properties:
                    try: 
                        has_property_type_uri = self.experiment.DYNAMAT.hasStrainGaugeProperty
                        property_name = self.experiment.DYNAMAT[f"SG_{property_type_uri.split('#')[-1]}"]
                        
                        spinbox = prop.get("spinbox")
                        combo_box = prop.get("combo_box") 
                        units_uri, _ = combo_box.currentData()
                        value = float(spinbox.value())

                        self.experiment.set_triple(str(property_name), str(self.experiment.RDF.type), 
                                       str(property_type_uri))
                        self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasUnits), units_uri)
                        self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasValue), value)
                        self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasDescription),
                                       f"{property_type_uri.split('#')[-1]} property of the strain gauges")
                        
                        self.experiment.add_instance_data(units_uri) # Add the units description
                        self.experiment.add_triple(str(testing_conditions_uri), self.experiment.DYNAMAT.hasStrainGaugeProperty,
                                                   property_name)  
                        
                    except: 
                         continue                        
                        
                    self.experiment.save()  




        
