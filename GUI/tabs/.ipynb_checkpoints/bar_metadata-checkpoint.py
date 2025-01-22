from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel, QComboBox, QDoubleSpinBox, QHBoxLayout, QScrollArea, QPushButton
)
from rdflib import Graph, Namespace, URIRef
from GUI.components.common_widgets import MaterialSelector, UnitSelector, DoubleSpinBox, SetDefaults
from GUI.components.common_widgets import SetUnitDefaults
from GUI.tabs.fea_metadata import FEAMetadataWindow
from config.bar_config import BarConfiguration

class BarMetadataWidget(QWidget):
    def __init__(self, ontology_path, test_config, experiment_temp_file):
        super().__init__()
        self.test_config = test_config
        self.experiment = experiment_temp_file
        self.bar_config = BarConfiguration()
        self.bar_properties = {} # Tracks properties and dimensions for each bar instance
        self.current_mode = URIRef(self.test_config.test_mode)

        self.ontology = Graph()
        self.ontology_path = ontology_path
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Tab Widget for Bars
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Populate tabs for bar instances
        self.populate_bar_tabs()
        
        # Confirm/Edit Button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.toggle_confirm_edit)
        self.layout.addWidget(self.confirm_button) 

    #################################################
    ## POPULATE BAR METADATA TABS
    #################################################
    
    def populate_bar_tabs(self):
        """Generate a tab for each Bar instance based on the ontology."""
        query = """
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?barInstance ?legendName WHERE {
            ?barInstance rdf:type :Bar ;
                         :hasLegendName ?legendName .
        }
        """
        try:
            results = self.ontology.query(query)
            for row in results:
                bar_instance_uri = str(row.barInstance)
                legend_name = str(row.legendName)            
                tab = self.create_bar_tab(bar_instance_uri, legend_name)
                self.tabs.addTab(tab, legend_name)
        except Exception as e:
            print(f"Error querying bar instances: {e}")

    def create_bar_tab(self, bar_instance_uri, legend_name):
        """Create a tab for a specific bar."""
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a content widget for the scroll area
        scroll_area_widget = QWidget()
        layout = QVBoxLayout()
        scroll_area_widget.setLayout(layout)

        # Add Dimensions
        dimensions_label = QLabel("Dimensions:")
        layout.addWidget(dimensions_label)
        self.add_fields(layout, bar_instance_uri, "Dimension")

        # Material Selector
        material_label = QLabel(f"{legend_name} Material:")
        layout.addWidget(material_label)
        material_selector = MaterialSelector(self.ontology_path, self.experiment.DYNAMAT.Material)
        SetDefaults(self.ontology_path, self.bar_config[f"{bar_instance_uri.split('#')[-1]}_Material"], material_selector)
        layout.addWidget(material_selector)
        self.bar_properties[bar_instance_uri].append({
            "material_selector": material_selector,
            })

        # Add Mechanical Properties
        mech_label = QLabel("Mechanical Properties:")
        layout.addWidget(mech_label)
        self.add_fields(layout, bar_instance_uri, "MechanicalProperty")        
        
        # FEA Metadata Button (Initially hidden)
        fea_button = QPushButton("Add FEA Metadata")  
        fea_button.setObjectName("fea_button")
        fea_button.clicked.connect(lambda: self.open_fea_metadata(bar_instance_uri))
        layout.addWidget(fea_button)
    
        # Set initial visibility
        self.update_fea_button_visibility()
        layout.addStretch()

        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(scroll_area_widget)        
        
        return scroll_area

    #################################################
    ## POPULATE BAR FIELDS
    #################################################

    def add_fields(self, layout, bar_instance_uri, property_type):
        """Add input fields for dimensions or mechanical properties."""
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?property ?propertyName WHERE {{
            <{bar_instance_uri}> :has{property_type} ?property .
            ?property a :{property_type} ;
                      :hasName ?propertyName .
        }}
        """
        try:
            results = self.ontology.query(query)
            for row in results:
                property_instance_uri = str(row.property)
                property_name = str(row.propertyName)
                
                # Create input field
                field_layout = QHBoxLayout()
                label = QLabel(f"{property_name}:")
                field_layout.addWidget(label)
                spinbox = DoubleSpinBox()
                combo_box = UnitSelector(self.ontology_path, property_instance_uri)  

                try: 
                    spinbox.setValue(
                        float(self.bar_config[f"{bar_instance_uri.split('#')[-1]}_{property_instance_uri.split('#')[-1]}_value"])) 
                    SetUnitDefaults(self.ontology_path, 
                                self.bar_config[f"{bar_instance_uri.split('#')[-1]}_{property_instance_uri.split('#')[-1]}_units"],
                                combo_box)
                except: 
                    print(f"Default values not found for: {property_instance_uri.split('#')[-1]}")
                    
                field_layout.addWidget(spinbox)
                field_layout.addWidget(combo_box)                                
                layout.addLayout(field_layout)

                # Store widget references in bar_properties
                if bar_instance_uri not in self.bar_properties:
                    self.bar_properties[bar_instance_uri] = []
                    
                self.bar_properties[bar_instance_uri].append({
                    "property_instance": property_instance_uri,
                    "property_type": property_type,
                    "spinbox": spinbox,
                    "combo_box": combo_box
                })
                
        except Exception as e:
            print(f"Error querying properties for {bar_instance_uri}: {e}")
                
        except Exception as e:
            print(f"Error querying properties for {bar_instance_uri}: {e}")   

    #################################################
    ## ADD DATA FIELDS TO RDF
    #################################################

    def toggle_confirm_edit(self):
        """Toggle between Confirm and Edit modes."""
        #self.test_name = self.test_config.test_name
        editable = self.confirm_button.text() == "Edit"
        # Toggle all widgets associated with the bar instance
        for bar_instance_uri in self.bar_properties:
            for prop in self.bar_properties[bar_instance_uri]:
                # Set spinbox and combo box editable or non-editable
                try:
                    prop["spinbox"].setEnabled(editable)
                    prop["combo_box"].setEnabled(editable)                    
                except: 
                    prop["material_selector"].setEnabled(editable)

        # Update the button text
        self.confirm_button.setText("Confirm" if editable else "Edit")

        if not editable:
            testing_conditions_uri = self.experiment.DYNAMAT["Testing_Conditions"]
            striker_bar_uri = self.experiment.DYNAMAT["Striker_Bar"]
            incident_bar_uri = self.experiment.DYNAMAT["Incident_Bar"]
            transmitted_bar_uri = self.experiment.DYNAMAT["Transmitted_Bar"]

            for bar_instance_uri, properties in self.bar_properties.items():

                # Chose the proper bar instance
                bar_name = bar_instance_uri.split("#")[-1]
                if bar_name.endswith("StrikerBar"):
                    #self.experiment.add_triple(str(striker_bar_uri), str(self.experiment.RDF.type), 
                    #                   str(self.experiment.DYNAMAT.StrikerBar))
                    #self.experiment.add_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasBar),
                    #                   striker_bar_uri)
                    ref_bar_uri = striker_bar_uri
                    
                elif bar_name.endswith("IncidentBar"):
                    self.experiment.add_triple(str(incident_bar_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.IncidentBar))
                    self.experiment.add_triple(str(incident_bar_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.Bar))
                    self.experiment.add_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasBar),
                                       incident_bar_uri)
                    ref_bar_uri = incident_bar_uri
                    
                elif bar_name.endswith("TransmittedBar"):
                    self.experiment.add_triple(str(transmitted_bar_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.TransmittedBar))
                    self.experiment.add_triple(str(transmitted_bar_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.Bar))
                    self.experiment.add_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasBar),
                                       transmitted_bar_uri)
                    ref_bar_uri = transmitted_bar_uri

                for prop in properties:
                    try: 
                        property_type = prop.get("property_type")
                        has_property_type_uri = self.experiment.DYNAMAT[f"has{property_type}"]
                        property_instance_uri = prop.get("property_instance")
                        property_name = self.experiment.DYNAMAT[f"{ref_bar_uri.split('#')[-1]}_{property_instance_uri.split('#')[-1]}"]
                        
                        spinbox = prop.get("spinbox")
                        combo_box = prop.get("combo_box") 
                        units_uri, _, _ = combo_box.currentData()
                        value = float(spinbox.value())

                        self.experiment.set_triple(str(property_name), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT[f"{property_type}"]))
                        self.experiment.add_triple(str(property_name), str(self.experiment.RDF.type), 
                                       str(property_instance_uri))
                        self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasUnits), units_uri)
                        self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasValue), value, obj_type = "float")
                        self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasDescription),
                                       f"{property_instance_uri.split('#')[-1]} of the {ref_bar_uri.split('#')[-1]}")
                        
                        self.experiment.add_instance_data(units_uri) # Add the units description
                        self.experiment.add_triple(str(ref_bar_uri), str(has_property_type_uri), property_name)  
                        
                    except: 
                        try:
                            material_selector = prop.get("material_selector")
                            material_uri, _ = material_selector.currentData()
                            self.experiment.set_triple(str(ref_bar_uri), str(self.experiment.DYNAMAT.hasMaterial), material_uri)
                            self.experiment.add_instance_data(material_uri)
                            self.experiment.add_triple(str(material_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.Material))
                        except: continue                        
                        
                self.experiment.save()                 

    #################################################
    ## ADD STRAIN GAUGE AND FEA TABS WHEN NEEDED
    #################################################

    def open_fea_metadata(self, bar_instance):
        #Open the FEA metadata window for the given bar instance.
        self.fea_metadata_window = FEAMetadataWindow(self.ontology_path, self.test_config, self.experiment, bar_instance)
        self.fea_metadata_window.show()

    def update_test_mode(self, test_mode):
        self.current_mode = URIRef(test_mode) if isinstance(test_mode, str) else self.current_mode
        #print(f"Current Mode = {self.current_mode}")
        self.update_fea_button_visibility()
        return 

    # Dynamic visibility for FEA button
    def update_fea_button_visibility(self):
        """Update the visibility of the FEA Metadata button based on the test mode."""
        is_fea_mode = self.current_mode == self.experiment.DYNAMAT.FEAMode
        for fea_button in self.findChildren(QPushButton, "fea_button"):
            #print(f"setting button visible = {is_fea_mode}")
            fea_button.setVisible(is_fea_mode)
            
        if hasattr(self, "gauge_tab"):
            gauge_tab_index = self.tabs.indexOf(self.gauge_tab)
            if is_fea_mode == False:
                # Add the SG Properties tab back if LAB is active
                if gauge_tab_index == -1:
                    self.tabs.addTab(self.gauge_tab, "SG Properties")   
            else:
                # Remove the SG Properties tab if FEA is active
                self.tabs.removeTab(gauge_tab_index)
                   

      

        










