from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QHBoxLayout, QDoubleSpinBox, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from rdflib import Graph, Namespace, URIRef
from GUI.tabs.fea_metadata import FEAMetadataWindow
from GUI.components.common_widgets import MaterialSelector, UnitSelector, DoubleSpinBox
from GUI.components.common_widgets import SetDefaults, ClassInstanceSelection, SetUnitDefaults
from config.specimen_config import SpecimenConfiguration
import numpy as np

class SpecimenMetadataWidget(QWidget):
    def __init__(self, ontology_path, test_config, experiment_temp_file):
        super().__init__()
        self.ontology_path = ontology_path
        self.test_config = test_config
        self.experiment = experiment_temp_file
        self.specimen_config = SpecimenConfiguration()
        self.current_type = URIRef(self.test_config.test_type)
        self.current_mode = URIRef(self.test_config.test_mode)        
        self.specimen_material = self.test_config.specimen_material

        self.originalDiameterSpinBox = None
        self.originalCrossSectionSpinBox = None

        self.deformedDiameterSpinBox = None
        self.deformedCrossSectionSpinBox = None

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.update_visibility()
        self.layout.addStretch()

    def populate_tab(self):
        # Material Selector        
        self.material_label = QLabel(f"Specimen Material: {self.specimen_material.split('#')[-1]}")
        self.layout.addWidget(self.material_label)

        # Add Dimensions Section
        self.dimensions_label = QLabel("Dimensions:")
        self.layout.addWidget(self.dimensions_label)
        self.add_fields(self.layout, self.experiment.DYNAMAT.SHPBSpecimen, "Dimension") 

        # Add Material Processing Section
        self.processing_label = QLabel("Material Processing:")
        self.processing_selector = ClassInstanceSelection(self.ontology_path, self.experiment.DYNAMAT.SpecimenProcessing)
        SetDefaults(self.ontology_path, self.specimen_config["SHPBSpecimen_SpecimenProcessing"],
                        self.processing_selector)
        self.layout.addWidget(self.processing_label)
        self.layout.addWidget(self.processing_selector)

        # Add Shape Properties Section
        self.shape_label = QLabel("Specimen Shape:")
        self.shape_selector = ClassInstanceSelection(self.ontology_path, self.experiment.DYNAMAT.Shape)
        SetDefaults(self.ontology_path, self.specimen_config["SHPBSpecimen_Shape"], self.shape_selector)
        self.layout.addWidget(self.shape_label)
        self.layout.addWidget(self.shape_selector)

        # Add Structure Properties Section
        self.structure_label = QLabel("Specimen Structure:")
        self.structure_selector = ClassInstanceSelection(self.ontology_path, self.experiment.DYNAMAT.Structure)        
        SetDefaults(self.ontology_path, self.specimen_config["SHPBSpecimen_Structure"], self.structure_selector)
        self.layout.addWidget(self.structure_label)
        self.layout.addWidget(self.structure_selector)

        # Add FEA Metadata Window
        self.fea_button = QPushButton("Add FEA Metadata")
        self.fea_button.clicked.connect(lambda: self.open_fea_metadata(self.experiment.DYNAMAT.SHPBSpecimen))
        self.layout.addWidget(self.fea_button)

        # Confirm/Edit Button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.toggle_confirm_edit)
        self.layout.addWidget(self.confirm_button) 

    #################################################
    ## CREATE SPECIMEN TABS
    #################################################
        
    def add_fields(self, layout, specimen_instance_uri, property_type):
        """Add input fields for dimensions or mechanical properties."""
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?property ?propertyName WHERE {{
            <{specimen_instance_uri}> :has{property_type} ?property .
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

                # For demonstration, store references to diameter/cross-section:
                if "OriginalDiameter" in property_instance_uri:
                    self.originalDiameterSpinBox = spinbox
                elif "OriginalCrossSectionalArea" in property_instance_uri:
                    self.originalCrossSectionSpinBox = spinbox

                elif "DeformedDiameter" in property_instance_uri:
                    self.deformedDiameterSpinBox = spinbox
                elif "DeformedCrossSectionalArea" in property_instance_uri:
                    self.deformedCrossSectionSpinBox = spinbox
                
                try:                     
                    SetUnitDefaults(self.ontology_path, 
                               self.specimen_config[f"{specimen_instance_uri.split('#')[-1]}_{property_instance_uri.split('#')[-1]}_units"],
                                combo_box)
                except: 
                    print(f"Default Specimen values not found for: {property_instance_uri.split('#')[-1]}")
                    
                field_layout.addWidget(spinbox)
                field_layout.addWidget(combo_box)                                
                layout.addLayout(field_layout)
                
                # Store widget references in bar_properties
                if property_instance_uri not in self.specimen_properties:
                    self.specimen_properties[property_instance_uri] = []   
                    
                self.specimen_properties[property_instance_uri].append({
                    "property_type": property_type,
                    "spinbox": spinbox,
                    "combo_box": combo_box
                })

                self._connect_diameter_signals()
                
        except Exception as e:
            print(f"Error querying properties for {property_instance_uri}: {e}")


    #################################################
    ## ADD DATA FIELDS TO RDF
    #################################################

    def toggle_confirm_edit(self):
        """Toggle between Confirm and Edit modes."""
        editable = self.confirm_button.text() == "Edit"
        # Toggle all widgets associated with the bar instance
        for specimen_uri in self.specimen_properties:
            for prop in self.specimen_properties[specimen_uri]:
                # Set spinbox and combo box editable or non-editable
                    prop["spinbox"].setEnabled(editable)
                    prop["combo_box"].setEnabled(editable)
                
        self.processing_selector.setEnabled(editable)
        self.shape_selector.setEnabled(editable)
        self.structure_selector.setEnabled(editable)            
                    
                    
        # Update the button text
        self.confirm_button.setText("Confirm" if editable else "Edit")
        
        if not editable:           
            specimen_uri = self.experiment.DYNAMAT["Test_Specimen"]

            try: 
                processing_uri, _ = self.processing_selector.currentData()
                self.experiment.set_triple(str(specimen_uri), str(self.experiment.DYNAMAT.hasSpecimenProcessing), processing_uri)
                self.experiment.add_instance_data(processing_uri)
            except: 
                None

            try: 
                shape_uri, _ = self.shape_selector.currentData()
                self.experiment.set_triple(str(specimen_uri), str(self.experiment.DYNAMAT.hasShape), shape_uri)
                self.experiment.add_instance_data(shape_uri)
            except: 
                None 

            try: 
                structure_uri, _ = self.structure_selector.currentData()
                self.experiment.set_triple(str(specimen_uri), str(self.experiment.DYNAMAT.hasStructure), structure_uri)
                self.experiment.add_instance_data(structure_uri)
            except: 
                None
            
            for specimen_property_uri, properties in self.specimen_properties.items():
                for prop in properties:
                    try: 
                        property_type = prop.get("property_type")
                        has_property_type_uri = self.experiment.DYNAMAT[f"has{property_type}"]
                        property_name = self.experiment.DYNAMAT[f"{specimen_uri.split('#')[-1]}_{specimen_property_uri.split('#')[-1]}"]
                            
                        spinbox = prop.get("spinbox")
                        combo_box = prop.get("combo_box") 
                        units_uri, _, _ = combo_box.currentData()
                        value = float(spinbox.value())
    
                        self.experiment.set_triple(str(property_name), str(self.experiment.RDF.type), 
                                        str(self.experiment.DYNAMAT[f"{property_type}"]))
                        self.experiment.add_triple(str(property_name), str(self.experiment.RDF.type), 
                                        str(specimen_property_uri))
                        self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasUnits), units_uri)
                        self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasValue), value, obj_type="float")
                        self.experiment.set_triple(str(property_name), str(self.experiment.DYNAMAT.hasDescription),
                                        f"{specimen_property_uri.split('#')[-1]} of the {specimen_uri.split('#')[-1]}")
                            
                        self.experiment.add_instance_data(units_uri) # Add the units description                    
                        self.experiment.add_triple(str(specimen_uri), str(has_property_type_uri), property_name)                          
                    except Exception as e: 
                        print(e)
                        
                self.experiment.save()  
    
    #################################################
    ## VISIBILITY CONTROL
    #################################################
            
    def update_visibility(self):
        """Update visibility of LAB and FEA specimen tabs."""
        # Find Current state of variables
        test_mode = self.current_mode
        test_type = self.current_type       
        
        if test_type == self.experiment.DYNAMAT.SpecimenTest:
            self.clear_layout(self.layout)
            self.specimen_properties = {}
            self.populate_tab()
            if test_mode == self.experiment.DYNAMAT.FEAMode:
                self.fea_button.setVisible(True)
            else: 
                self.processing_selector.setEnabled(True)
                self.fea_button.setVisible(False)
        else:
            # Clear all widgets in the tab's layout to make it "blank"
            self.clear_layout(self.layout)
            print("No Specimen Option shown, because Pulse Test is currently selected")

    def open_fea_metadata(self, specimen_instance):
        """Open the FEA metadata window for the given bar instance."""
        self.fea_metadata_window = FEAMetadataWindow(self.ontology_path, self.test_config, self.experiment, specimen_instance)
        self.fea_metadata_window.show()

    def update_test_type(self, test_type):
        self.current_type = URIRef(test_type) if isinstance(test_type, str) else self.current_type
        print(f"Current Test Type = {self.current_type}")
        self.update_visibility()
        return 

    def update_test_mode(self, test_mode):
        self.current_mode = URIRef(test_mode) if isinstance(test_mode, str) else self.current_mode
        print(f"Current Test Mode = {self.current_mode}")
        self.update_visibility()
        return 

    def update_specimen_material(self, current_specimen_material):
        self.material_label.setText(f"Specimen Material: {current_specimen_material}")
        return 

    def _connect_diameter_signals(self):
        """
        Once we have references to both the diameter and cross-section spinboxes,
        connect their signals so that changing the diameter auto-updates cross-section.
        """

        # If we have an OriginalDiameter and OriginalCrossSection, connect them:
        if self.originalDiameterSpinBox and self.originalCrossSectionSpinBox:
            self.originalDiameterSpinBox.valueChanged.connect(
                lambda val: self.update_spcimen_dimensions(
                    self.originalDiameterSpinBox,
                    self.originalCrossSectionSpinBox
                )
            )
        

        # If we have a DeformedDiameter and DeformedCrossSection, connect them:
        if self.deformedDiameterSpinBox and self.deformedCrossSectionSpinBox:
            self.deformedDiameterSpinBox.valueChanged.connect(
                lambda val: self.update_spcimen_dimensions(
                    self.deformedDiameterSpinBox,
                    self.deformedCrossSectionSpinBox
                )
            )

    def update_spcimen_dimensions(self, diameter_spinbox, cross_section_spinbox):
        """
        Compute cross-sectional area if the shape is cylindrical
        based on the given diameter spinbox, and update cross_section_spinbox.
        """
        shape_uri, shape_label = self.shape_selector.currentData()

        if "Cylindrical" in shape_label or "Cylindrical" in shape_uri:
            diameter_value = diameter_spinbox.value()
            if diameter_value and diameter_value > 0:
                cross_section = np.pi * (diameter_value / 2) ** 2
                cross_section_spinbox.setValue(cross_section)
                print(f"[INFO] Recalculated cross-section = {cross_section:.4f}")
            else:
                print("[WARNING] Diameter is zero or unset. Cannot compute cross-section.")
                
        else:
            print("[INFO] Shape is not cylindrical; skipping cross-section calculation.")
            
        
        
    def clear_layout(self, layout):
        """Recursively clear all widgets and sublayouts from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            # Check for widget
            if widget := item.widget():
                widget.deleteLater()
            # Check for sublayout
            elif sub_layout := item.layout():
                self.clear_layout(sub_layout)
                # Delete the sublayout after clearing it
                del sub_layout


        
        