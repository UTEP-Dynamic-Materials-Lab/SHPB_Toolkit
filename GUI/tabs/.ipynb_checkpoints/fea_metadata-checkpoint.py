from PyQt6.QtWidgets import  QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDoubleSpinBox
from PyQt6.QtWidgets import  QComboBox, QRadioButton, QButtonGroup, QPushButton, QScrollArea
from PyQt6.QtCore import Qt
from rdflib import Graph, Namespace, URIRef
from GUI.components.common_widgets import ClassInstanceSelection, UnitSelector, DoubleSpinBox, SetDefaults, FiniteElementSelector
from GUI.components.common_widgets import SetUnitDefaults
from config.fea_config import FEAConfiguration

class FEAMetadataWindow(QMainWindow):
    def __init__(self, ontology_path, test_config, experiment_temp_file, object_instance):
        super().__init__()
        self.setWindowTitle(f"FEA Metadata for {object_instance.split('#')[-1]}")
        self.setGeometry(100, 100, 600, 450)
        self.ontology_path = ontology_path
        self.experiment = experiment_temp_file
        self.test_config = test_config
        self.fea_config = FEAConfiguration()
        self.object_instance = object_instance
        self.model_parameters = {}

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
        # Main Layout
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Finite Element Selection 
        # Add the finite element label and selector
        element_label = QLabel("Select Finite Element Type:") 
        self.layout.addWidget(element_label)
        self.element_selector = FiniteElementSelector(self.ontology_path, self.experiment.DYNAMAT.FiniteElement)
        self.layout.addWidget(self.element_selector)
        
        # Create a horizontal layout for size and unit selection
        size_unit_layout = QHBoxLayout()
        
        # Add the element size label and spin box
        size_label = QLabel("Element Size:")
        size_unit_layout.addWidget(size_label)
        self.element_size_box = DoubleSpinBox()
        size_unit_layout.addWidget(self.element_size_box)
        
        # Add the element unit label and selector
        unit_label = QLabel("Units:")
        size_unit_layout.addWidget(unit_label)
        self.element_unit_selector = UnitSelector(self.ontology_path, self.experiment.DYNAMAT.ElementSize)
        size_unit_layout.addWidget(self.element_unit_selector)
        
        # Add the horizontal layout to the main layout
        self.layout.addLayout(size_unit_layout)        
        
        # Model Selection
        model_label = QLabel("Select Strength Model:")
        self.layout.addWidget(model_label)
        
        self.model_combo = ClassInstanceSelection(self.ontology_path, self.experiment.DYNAMAT.StrengthModel)
        SetDefaults(self.ontology_path, 
                    self.fea_config[f"{self.object_instance.split('#')[-1]}_Model"],
                    self.model_combo)
        self.model_combo.currentIndexChanged.connect(self.populate_parameters)  # Update parameters on selection change
        self.layout.addWidget(self.model_combo)
        
        # Parameter Section
        parameter_section_label = QLabel("Parameters:")
        self.layout.addWidget(parameter_section_label)
        
        # Scroll Area for Parameters
        self.parameter_scroll_area = QScrollArea()
        self.parameter_scroll_area.setWidgetResizable(True)  # Make the scroll area resizable
        self.parameter_widget = QWidget()
        self.parameter_layout = QVBoxLayout(self.parameter_widget)
        self.parameter_scroll_area.setWidget(self.parameter_widget)
        self.layout.addWidget(self.parameter_scroll_area)
        
        # Populate Parameters for the Selected Model
        self.populate_parameters()

        # Confirm Button 
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.toggle_confirm)
        self.confirm_button.clicked.connect(self.close)
        self.layout.addWidget(self.confirm_button) 
        
    #################################################
    ## Populate Parameters Based on Strength Model
    #################################################

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
        model_instance_uri, _ = self.model_combo.currentData()
        
        if model_instance_uri:
            query = f"""
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT ?parameter ?paramName WHERE {{
                <{model_instance_uri}> :hasParameter ?parameter .
                ?parameter :hasName ?paramName .
            }}
            """
            results = self.ontology.query(query)       
       
            for row in results:
                parameter_uri = str(row.parameter)
                param_name = str(row.paramName)      
      
                # Build entry fields
                param_label = QLabel(f"{param_name}:")   
                spinbox = DoubleSpinBox()
                
                try:
                    spinbox.setValue(
                        float(self.fea_config[f"{self.object_instance.split('#')[-1]}_{parameter_uri.split('#')[-1]}_value"]))
                except: 
                    None
        
                # Unit selector (QComboBox)
                unit_combo = UnitSelector(self.ontology_path, parameter_uri)
                try:
                    SetUnitDefaults(self.ontology_path, 
                                self.fea_config[f"{self.object_instance.split('#')[-1]}_{parameter_uri.split('#')[-1]}_units"],
                                unit_combo)
                except: 
                    None
        
                # Add parameter layout
                param_layout = QHBoxLayout()
                param_layout.addWidget(param_label)
                param_layout.addWidget(spinbox)
                param_layout.addWidget(unit_combo)
                
                self.parameter_layout.addLayout(param_layout)

                # Store widget references in bar_properties
                if model_instance_uri not in self.model_parameters:
                    self.model_parameters[model_instance_uri] = []
                    
                self.model_parameters[model_instance_uri].append({
                    "parameter_instance": parameter_uri,
                    "parameter_name": param_name,
                    "spinbox": spinbox,
                    "combo_box": unit_combo
                })
                
        else:
            # If no model is selected, print a message
            print("No model instance selected. Parameter fields cleared.")

    #################################################
    ## ADD DATA FIELDS TO RDF
    #################################################
    def toggle_confirm(self):
        """Toggle between Confirm and Edit modes."""
        testing_conditions_uri = self.experiment.DYNAMAT["Testing_Conditions"]
        striker_bar_uri = self.experiment.DYNAMAT["Striker_Bar"]
        incident_bar_uri = self.experiment.DYNAMAT["Incident_Bar"]
        transmitted_bar_uri = self.experiment.DYNAMAT["Transmitted_Bar"]
        specimen_uri = self.experiment.DYNAMAT["Test_Specimen"]

        for model_instance_uri, parameters in self.model_parameters.items():

            # Chose the proper bar instance
            object_instance_ref = self.object_instance.split("#")[-1]
            if object_instance_ref.endswith("StrikerBar"):
                self.experiment.add_triple(str(striker_bar_uri), str(self.experiment.RDF.type), 
                                   str(self.experiment.DYNAMAT.StrikerBar))
                self.experiment.add_triple(str(striker_bar_uri), str(self.experiment.RDF.type), 
                                   str(self.experiment.DYNAMAT.Bar))
                self.experiment.add_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasBar),
                                   striker_bar_uri)
                ref_bar_uri = striker_bar_uri
                    
            elif object_instance_ref.endswith("IncidentBar"):
                self.experiment.add_triple(str(incident_bar_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.IncidentBar))
                self.experiment.add_triple(str(incident_bar_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.Bar))
                self.experiment.add_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasBar),
                                       incident_bar_uri)
                ref_bar_uri = incident_bar_uri
                    
            elif object_instance_ref.endswith("TransmittedBar"):
                self.experiment.add_triple(str(transmitted_bar_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.TransmittedBar))
                self.experiment.add_triple(str(transmitted_bar_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.Bar))
                self.experiment.add_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasBar),
                                       transmitted_bar_uri)
                ref_bar_uri = transmitted_bar_uri

            elif object_instance_ref.endswith("Specimen"):
                ref_bar_uri = specimen_uri

            # Adds Strength Model to Object Instance
            fea_metadata_uri = self.experiment.DYNAMAT[f"{ref_bar_uri.split('#')[-1]}_FEA_Metadata"]
            model_name_uri = self.experiment.DYNAMAT[f"{ref_bar_uri.split('#')[-1]}_FEA_Strength_Model"]
            element_name_uri = self.experiment.DYNAMAT[f"{ref_bar_uri.split('#')[-1]}_FEA_Element"]
            
            self.experiment.set_triple(fea_metadata_uri, str(self.experiment.RDF.type), str(self.experiment.DYNAMAT.FEAMetadata))
            self.experiment.add_triple(ref_bar_uri, self.experiment.DYNAMAT.hasFEAMetadata, fea_metadata_uri)
            
            self.experiment.set_triple(model_name_uri, str(self.experiment.RDF.type), str(model_instance_uri))
            self.experiment.add_triple(model_name_uri, str(self.experiment.RDF.type), str(self.experiment.DYNAMAT.StrengthModel))
            self.experiment.set_triple(fea_metadata_uri, str(self.experiment.DYNAMAT.hasStrengthModel), str(model_name_uri))

            element_uri = self.element_selector.currentData()
            element_size_value = float(self.element_size_box.value())
            element_size_units, _, _ = self.element_unit_selector.currentData()
            
            self.experiment.set_triple(element_name_uri, str(self.experiment.RDF.type), str(element_uri))
            self.experiment.add_triple(element_name_uri, str(self.experiment.RDF.type), str(self.experiment.DYNAMAT.FiniteElement))
            self.experiment.set_triple(fea_metadata_uri, str(self.experiment.DYNAMAT.hasFiniteElement), str(element_name_uri))
            
            element_size_uri = self.experiment.DYNAMAT[f"{ref_bar_uri.split('#')[-1]}_FEA_Element_Size"]
            
            self.experiment.set_triple(element_size_uri, str(self.experiment.RDF.type), str(self.experiment.DYNAMAT.ElementSize))
            self.experiment.add_triple(element_size_uri, str(self.experiment.RDF.type), str(self.experiment.DYNAMAT.Dimension))
            self.experiment.set_triple(element_size_uri, str(self.experiment.DYNAMAT.hasValue), element_size_value, obj_type = "float")
            self.experiment.set_triple(element_size_uri, str(self.experiment.DYNAMAT.hasUnits), element_size_units)
            self.experiment.add_instance_data(element_size_units)            
            self.experiment.set_triple(element_name_uri, str(self.experiment.DYNAMAT.hasDimension), str(element_size_uri))

            for param in parameters:
                try: 
                    property_type = self.experiment.DYNAMAT.MechanicalProperty
                    has_property_type_uri = self.experiment.DYNAMAT.hasParameter
                    property_instance_uri = param.get("parameter_instance")
                    print(property_instance_uri)
                    property_name = self.experiment.DYNAMAT[f"{model_name_uri.split('#')[-1]}_{property_instance_uri.split('#')[-1]}"]
                        
                    spinbox = param.get("spinbox")
                    combo_box = param.get("combo_box") 
                    units_uri, _, _ = combo_box.currentData()
                    value = float(spinbox.value())

                    self.experiment.set_triple(str(property_name), str(self.experiment.RDF.type), 
                                    str(property_instance_uri))
                    self.experiment.add_triple(str(property_name), str(self.experiment.RDF.type), 
                                    str(property_type))
                    self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasUnits), units_uri)
                    self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasValue), value, obj_type = "float")
                    self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasDescription),
                                    f"{property_instance_uri.split('#')[-1]} of the {model_name_uri.split('#')[-1]}")
                        
                    self.experiment.add_instance_data(units_uri) # Add the units description
                    self.experiment.add_triple(str(model_name_uri), self.experiment.DYNAMAT.hasParameter, property_name)  
                        
                except: 
                    continue
                        
            self.experiment.save() 
