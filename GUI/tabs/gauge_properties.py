from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QDoubleSpinBox, QComboBox, QHBoxLayout, QScrollArea, QPushButton, QSpinBox
)
from PyQt6.QtCore import Qt
from rdflib import Graph, Namespace, URIRef
from GUI.components.common_widgets import ClassInstanceSelection, UnitSelector, DoubleSpinBox, SetDefaults, SetUnitDefaults
from config.strain_gauge_config import SGConfiguration

class GaugePropertiesWidget(QWidget):
    def __init__(self, ontology_path, test_config, experiment_temp_file):
        super().__init__()
        self.ontology_path = ontology_path        
        self.experiment = experiment_temp_file
        self.test_config = test_config
        self.sg_config = SGConfiguration()
        self.property_info = {} # Tracks Gauge Properties
        self.distance_info = {} # Tracks Gauge Distances
        self.signal_spinboxes = {}  # Tracks Gauge Numbers
        self.bar_list = [self.experiment.DYNAMAT.Incident_Bar, self.experiment.DYNAMAT.Transmitted_Bar]
        self.signal_labels = ["Incident Bar", "Transmitted Bar"]
        self.current_mode = URIRef(self.test_config.test_mode)
        

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)   

        signal_label = QLabel("Define Number of Signals for Each Sensor:")
        self.layout.addWidget(signal_label)

        self.init_ui()

        # Confirm/Edit Button
        self.confirm_button = QPushButton("Confirm SG Properties")
        self.confirm_button.clicked.connect(self.toggle_confirm_edit)
        self.layout.addWidget(self.confirm_button) 

        self.update_visibility()
        

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
        
        for idx, label in enumerate(self.signal_labels):
            sensor_layout = QHBoxLayout()
            sensor_label = QLabel(f"{label} Strain Gauges:")
            spinbox = QSpinBox()
            spinbox.setRange(0, 100)  # Adjust range as needed
            try: 
                spinbox.setValue(int(self.sg_config[f"{URIRef(self.bar_list[idx]).split('#')[-1]}_Gauges"]))
            except Exception as e:
                print(f"No default number of strain gauges found for: {label}")
                print(e)
    
            sensor_layout.addWidget(sensor_label)
            sensor_layout.addWidget(spinbox)
            self.layout.addLayout(sensor_layout)
    
            # Store spinbox reference
            self.signal_spinboxes[URIRef(self.bar_list[idx])] = spinbox
            
        self.generate_mapping_fields(scroll_layout) # Prepopulate with default fields
        
        # Continue button
        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(lambda: self.generate_mapping_fields(scroll_layout))
        self.layout.addWidget(self.continue_button)        

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
                SetUnitDefaults(self.ontology_path, 
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
                "label": label,
                "spinbox": spinbox,
                "combo_box": unit_combo
                })

    #################################################
    ## ADD DATA FIELDS TO RDF
    #################################################
    def toggle_confirm_edit(self):
        """Toggle between Confirm and Edit modes."""
        
        editable = self.confirm_button.text() == "Edit SG Properties"
        self.continue_button.setEnabled(editable)
        for _, prop in self.signal_spinboxes.items():
            # Set spinbox and combo box editable or non-editable
            try:
                prop.setEnabled(editable)                   
            except: 
                continue

        for property_type_uri in self.property_info:
            for prop in self.property_info[property_type_uri]:
                # Set spinbox and combo box editable or non-editable
                try:
                    prop["spinbox"].setEnabled(editable)
                    prop["combo_box"].setEnabled(editable)                    
                except: 
                    continue
                    
        for property_type_uri in self.distance_info:
            for prop in self.distance_info[property_type_uri]:
                # Set spinbox and combo box editable or non-editable
                try:
                    prop["spinbox"].setEnabled(editable)
                    prop["unit_box"].setEnabled(editable)                    
                except: 
                    continue

        
        # Update the button text
        self.confirm_button.setText("Confirm SG Properties" if editable else "Edit SG Properties")

        if not editable:
            #testing_conditions_uri = self.experiment.DYNAMAT["Testing_Conditions"]

            for sg_instance_uri, distance_dic in self.distance_info.items():
                for dist in distance_dic:
                    bar_name = dist.get("bar_instance_uri")
                    sg_distance_value = float(dist.get("spinbox").value())
                    sg_distance_unit_uri, _, _= dist.get("unit_box").currentData()
                    sg_distance_uri = f"{sg_instance_uri}_Distance"
                
                    self.experiment.set_triple(str(sg_instance_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.SHPBStrainGauge))  
                
                    self.experiment.set_triple(str(sg_distance_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.StrainGaugeDistance)) 
                    self.experiment.add_triple(str(sg_distance_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.Dimension))
                    self.experiment.add_triple(str(sg_distance_uri), str(self.experiment.DYNAMAT.hasValue), 
                                       sg_distance_value, obj_type = "float")
                    self.experiment.add_triple(str(sg_distance_uri), str(self.experiment.DYNAMAT.hasUnits), 
                                       sg_distance_unit_uri)
                    self.experiment.add_instance_data(sg_distance_unit_uri)
                
                    self.experiment.set_triple(str(sg_instance_uri), str(self.experiment.DYNAMAT.hasDimension), 
                                       str(sg_distance_uri))
                    self.experiment.add_triple(str(bar_name), str(self.experiment.DYNAMAT.hasStrainGauge), 
                                       str(sg_instance_uri))
                
                    for property_type_uri, properties in self.property_info.items():                
                        for prop in properties:
                            try: 
                                has_property_type_uri = self.experiment.DYNAMAT.hasStrainGaugeProperty
                                property_name = self.experiment.DYNAMAT[f"SG_{property_type_uri.split('#')[-1]}"]
                        
                                spinbox = prop.get("spinbox")
                                combo_box = prop.get("combo_box") 
                                units_uri, _, _ = combo_box.currentData()
                                value = float(spinbox.value())

                                self.experiment.set_triple(str(property_name), str(self.experiment.RDF.type), 
                                       str(property_type_uri))
                                self.experiment.add_triple(str(property_name), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.StrainGaugeProperty))
                                self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasUnits), units_uri)
                                self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasValue),
                                                           value, obj_type = "float")
                                self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasDescription),
                                       f"{property_type_uri.split('#')[-1]} property of the strain gauges")
                        
                                self.experiment.add_instance_data(units_uri) # Add the units description
                                self.experiment.add_triple(str(sg_instance_uri), self.experiment.DYNAMAT.hasStrainGaugeProperty,
                                                   property_name)  
                        
                            except: 
                                 continue                        
                        
                self.experiment.save()  


    def generate_mapping_fields(self, layout):
        """Create dropdowns for mapping file columns to signals."""
        # Track widgets created by this function
        if not hasattr(self, 'generated_widgets'):
            self.generated_widgets = []
    
        # Clear previously created widgets
        for widget in self.generated_widgets:
            widget.setParent(None)
        self.generated_widgets.clear()
    
        idx = 0
        for signal_instance_uri, spinbox in self.signal_spinboxes.items():
            signal_count = spinbox.value()
            if signal_count > 0:
                for i in range(signal_count):
                    # Label for the signal
                    signal_name = self.signal_labels[idx]
                    signal_label = QLabel(f"{signal_name} {i} Strain Gauge Distance:")
                    signal_name_uri = self.experiment.DYNAMAT[f"{signal_instance_uri.split('#')[-1][:-4]}StrainGauge_{i}"]
    
                    # ComboBox for units
                    value_spinbox = DoubleSpinBox()                    
                    unit_combo = UnitSelector(self.ontology_path, self.experiment.DYNAMAT.StrainGaugeDistance)
                    try: 
                        value_spinbox.setValue(float(self.sg_config[f"{signal_name_uri.split('#')[-1]}_Distance_value"]))
                        SetUnitDefaults(self.ontology_path, 
                            self.sg_config[f"{signal_name_uri.split('#')[-1]}_Distance_units"],
                            unit_combo)
                    except Exception as e: 
                        print(e)
                        print(f"No default distance values found for: {signal_name_uri.split('#')[-1]}_Distance_value")
    
                    # Layout for the signal mapping
                    field_layout = QHBoxLayout()
                    field_layout.addWidget(signal_label)
                    field_layout.addWidget(value_spinbox)
                    field_layout.addWidget(unit_combo)
    
                    # Add layout to the parent layout
                    layout.addLayout(field_layout)
    
                    # Store created widgets for cleanup later
                    self.generated_widgets.extend([signal_label, value_spinbox, unit_combo])
    
                    # Store widget references in property_info
                    if signal_name_uri not in self.distance_info:
                        self.distance_info[signal_name_uri] = []
    
                    self.distance_info[signal_name_uri].append({
                        "bar_instance_uri": signal_instance_uri,
                        "spinbox": value_spinbox,
                        "unit_box": unit_combo
                    })
    
            idx += 1

    def update_test_mode(self, test_mode):
        self.current_mode = URIRef(test_mode) if isinstance(test_mode, str) else self.current_mode
        print(f"Current Test Mode = {self.current_mode}")
        self.update_visibility()
        return 

    def update_visibility(self):
        """Update visibility of LAB and FEA specimen tabs."""
        # Find Current state of variables
        test_mode = self.current_mode      
        
        if test_mode == self.experiment.DYNAMAT.FEAMode:
            for property_type_uri, properties in self.property_info.items():
                for prop in properties:
                    # Set spinbox and combo box editable or non-editable
                    try:
                        if URIRef(property_type_uri) != self.experiment.DYNAMAT.DataAcquisitionRate:
                            prop["label"].setVisible(False)
                            prop["spinbox"].setVisible(False)
                            prop["combo_box"].setVisible(False)                  
                    except: 
                        continue
        else: 
            for property_type_uri in self.property_info:
                for prop in self.property_info[property_type_uri]:
                    # Set spinbox and combo box editable or non-editable
                    try:
                        prop["label"].setVisible(True)
                        prop["spinbox"].setVisible(True)
                        prop["combo_box"].setVisible(True)                  
                    except: 
                        continue