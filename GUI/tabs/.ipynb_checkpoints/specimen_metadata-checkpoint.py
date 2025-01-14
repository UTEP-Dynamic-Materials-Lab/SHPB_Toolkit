from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QHBoxLayout, QDoubleSpinBox, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from rdflib import Graph, Namespace
from GUI.tabs.fea_metadata import FEAMetadataWindow
#from GUI.components.common_widgets import MaterialSelector

class SpecimenMetadataWidget(QWidget):
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

        # Tab Widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Populate Specimen Tabs
        self.lab_specimen_tab = self.create_specimen_tab("LABSpecimen", "LAB Specimen")
        self.fea_specimen_tab = self.create_specimen_tab("FEASpecimen", "FEA Specimen")

        self.tabs.addTab(self.lab_specimen_tab, "LAB Specimen")
        
    def create_specimen_tab(self, specimen_instance, legend_name):
        """Create a tab for a specific specimen."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Material Selector
        material_selector = MaterialSelector(self.ontology_path, self.test_config)
        layout.addWidget(material_selector)

        # Add Material Processing Section
        if specimen_instance == "LABSpecimen":
            self.add_property_selector(layout, specimen_instance, "MaterialProcessing", "Material Processing")
    
        # Add Dimensions Section
        dimensions_label = QLabel("Dimensions:")
        layout.addWidget(dimensions_label)
        self.add_fields(layout, specimen_instance, "Dimension")  

        # Add Shape Properties Section
        self.add_property_selector(layout, specimen_instance, "Shape", "Shape")

        # Add Structure Properties Section
        self.add_property_selector(layout, specimen_instance, "Structure", "Structure")
    
        # FEA Metadata Button (Initially hidden)
        fea_button = QPushButton("Add FEA Metadata")
        fea_button.clicked.connect(lambda: self.open_fea_metadata(specimen_instance))
        fea_button.setVisible(self.test_config.is_fea)  # Show only if FEA mode is active
        layout.addWidget(fea_button)
    
        # Define toggle_fea_options dynamically for this tab
        def toggle_fea_options(is_fea):
            """Toggle the visibility of the FEA button."""
            fea_button.setVisible(is_fea)
            print(f"FEA options toggled for {legend_name}: {'Visible' if is_fea else 'Hidden'}")
    
        # Attach the toggle method to the tab
        tab.toggle_fea_options = toggle_fea_options
    
        tab.setLayout(layout)
        return tab


    def add_fields(self, layout, specimen_instance, property_type):
        """Add input fields for dimensions or mechanical properties."""
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?property ?propertyName WHERE {{
            <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#{specimen_instance}> :has{property_type} 
            ?property .
            ?property a :{property_type} ;
                      :hasName ?propertyName .
        }}
        """
        try:
            results = self.ontology.query(query)
            if not results:
                print(f"No {property_type} found for {specimen_instance}")
            for row in results:
                property_instance = str(row.property)
                property_name = str(row.propertyName)
                layout.addLayout(self.create_input_field(specimen_instance, property_instance, property_name))
        except Exception as e:
            print(f"Error querying {property_type} for {specimen_instance}: {e}")


    def create_input_field(self, specimen_instance, property_instance, property_name):
        """Create an input field for a given property."""
        layout = QHBoxLayout()
        label = QLabel(f"{property_name}:")
        spinbox = QDoubleSpinBox()
        spinbox.setRange(0.0, 1e6)
        spinbox.setDecimals(4)

        # Set default value from config (optional)
        #default_value = self.get_default_value(specimen_instance, property_instance)
        #if default_value is not None:
        #    spinbox.setValue(default_value)

        combo_box = QComboBox()
        self.populate_units(property_instance, combo_box)
        """
        # Set default unit from config (optional)
        default_unit_abbreviation = self.get_default_unit(specimen_instance, property_instance)
        if default_unit_abbreviation:
            index = combo_box.findText(default_unit_abbreviation)
            if index >= 0:
                combo_box.setCurrentIndex(index)
        """
        layout.addWidget(label)
        layout.addWidget(spinbox)
        layout.addWidget(combo_box)
                
        return layout

    def populate_units(self, property_instance, combo_box):
        """Populate units for a given property."""
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?unit ?unitAbbreviation WHERE {{
            <{property_instance}> :hasUnits ?unit .
            ?unit :hasAbbreviation ?unitAbbreviation .
        }}
        """
        try:
            results = self.ontology.query(query)
            combo_box.clear()
            for row in results:
                unit_abbreviation = str(row.unitAbbreviation)
                combo_box.addItem(unit_abbreviation)
        except Exception as e:
            print(f"Error populating units for {property_instance}: {e}")

    def add_property_selector(self, layout, specimen_instance, property_type, property_legend):
        """
        Add a single combo box for selecting instances of a property type (e.g., Shape, Structure).
        """
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?instance ?instanceName WHERE {{
            ?instance a :{property_type} ;
                      :hasName ?instanceName .
        }}
        """
        try:
            results = self.ontology.query(query)
    
            if not results:
                print(f"No instances found for property type {property_type}")
                return
    
            # Create label and combo box
            label = QLabel(f"Select {property_legend}:")
            combo_box = QComboBox()
    
            # Populate combo box with instance names
            for row in results:
                instance_name = str(row.instanceName)
                instance_uri = str(row.instance)
                combo_box.addItem(instance_name, instance_uri)
    
            # Add label and combo box to the layout
            layout.addWidget(label)
            layout.addWidget(combo_box)
    
            # Optionally store the combo box for later retrieval of selected values
            setattr(self, f"{property_type.lower()}_selector", combo_box)
    
        except Exception as e:
            print(f"Error querying instances for property type {property_type}: {e}")
       

    def update_visibility(self, is_fea):
        """Update visibility of LAB and FEA specimen tabs."""
        print(f"Updating visibility in SpecimenMetadataWidget. is_fea: {is_fea}")
        
        # Remove and re-add tabs as needed
        fea_tab_index = self.tabs.indexOf(self.fea_specimen_tab)
        lab_tab_index = self.tabs.indexOf(self.lab_specimen_tab)
        
        if is_fea:
            # Ensure LAB tab is removed and FEA tab is added
            if lab_tab_index != -1:
                self.tabs.removeTab(lab_tab_index)
            if fea_tab_index == -1:
                self.tabs.addTab(self.fea_specimen_tab, "FEA Specimen")
        else:
            # Ensure FEA tab is removed and LAB tab is added
            if fea_tab_index != -1:
                self.tabs.removeTab(fea_tab_index)
            if lab_tab_index == -1:
                self.tabs.addTab(self.lab_specimen_tab, "LAB Specimen")

        # Iterate over all tabs and toggle their visibility based on the `is_fea` flag
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, "toggle_fea_options"):
                tab.toggle_fea_options(is_fea)

    def open_fea_metadata(self, specimen_instance):
        """Open the FEA metadata window for the given bar instance."""
        self.fea_metadata_window = FEAMetadataWindow(self.ontology_path, self.test_config, specimen_instance)
        self.fea_metadata_window.show()



