from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel, QComboBox, QDoubleSpinBox, QHBoxLayout
)
from rdflib import Graph, Namespace
from GUI.components.common_widgets import MaterialSelector
from config.bar_config import DEFAULT_BAR_CONFIG


class BarMetadataWidget(QWidget):
    def __init__(self, ontology_path, test_config):
        super().__init__()
        self.ontology_path = ontology_path
        self.test_config = test_config

        # Load Ontology
        self.ontology = Graph()
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Generate tabs for bars
        self.populate_bar_tabs()

    def populate_bar_tabs(self):
        """Generate a tab for each bar based on the ontology."""
        query = """
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?barInstance ?legendName WHERE {
            ?barInstance rdf:type :Bar ;
                         :hasLegendName ?legendName .
        }
        """
        results = self.ontology.query(query)
        for row in results:
            bar_instance = str(row.barInstance).split("#")[-1]
            legend_name = str(row.legendName)
            tab = self.create_bar_tab(bar_instance, legend_name)
            self.tabs.addTab(tab, legend_name)

    def create_bar_tab(self, bar_instance, legend_name):
        """Create a tab for a specific bar with its metadata."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Material Selector
        material_label = QLabel("Material:")
        material_selector = MaterialSelector(self.ontology_path, self.test_config)
        layout.addWidget(material_label)
        layout.addWidget(material_selector)

        # Dimensions Section
        dimension_label = QLabel("Dimensions:")
        layout.addWidget(dimension_label)
        dimensions = DEFAULT_BAR_CONFIG.get(bar_instance, {}).get("dimensions", {})
        for dimension, properties in dimensions.items():
            layout.addLayout(self.create_input_field(dimension, properties, is_dimension=True))
        
        # Mechanical Properties Section
        mech_label = QLabel("Mechanical Properties:")
        layout.addWidget(mech_label)
        mech_properties = DEFAULT_BAR_CONFIG.get(bar_instance, {}).get("mechanical_properties", {})
        for mech_property, properties in mech_properties.items():
            layout.addLayout(self.create_input_field(mech_property, properties, is_dimension=False))
        tab.setLayout(layout)
        return tab

    def create_input_field(self, name, properties, is_dimension=True):
        """Create an input field with a value and a unit selector."""
        layout = QHBoxLayout()
        label = QLabel(f"{name}:")
        
        # Create value input (spinbox)
        spinbox = QDoubleSpinBox()
        spinbox.setRange(0.0, 1e6)
        spinbox.setDecimals(4)
        if properties and "value" in properties:
            spinbox.setValue(properties["value"])
        
        # Create unit selector (combo box)
        combo_box = QComboBox()
        if properties and "unit" in properties:
            combo_box.addItem(properties["unit"])
    
        # Populate units using ontology query
        if is_dimension:
            self.populate_dimension_units(name, combo_box)
        else:
            self.populate_mechanical_units(name, combo_box)
        
        layout.addWidget(label)
        layout.addWidget(spinbox)
        layout.addWidget(combo_box)
        return layout
    
    def populate_dimension_units(self, entity, combo_box):
        """Populate unit options for a given dimension entity."""
        # Replace spaces with underscores or encode the entity
        entity_uri = self.namespace[entity.replace(" ", "_")]
        query = f"""
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?unitSymbol WHERE {{
            <{entity_uri}> rdf:type :Dimension ;
                            :hasUnits ?unit .
            ?unit :hasAbbreviation ?unitSymbol .
        }}
        """
        try:
            results = self.ontology.query(query)
            combo_box.clear()
            for row in results:
                combo_box.addItem(str(row.unitSymbol).strip())
        except Exception as e:
            print(f"Error populating units for {entity}: {e}")
    
    
    def populate_mechanical_units(self, entity, combo_box):
        """Populate unit options for a given mechanical property entity."""
        # Replace spaces with underscores or encode the entity
        entity_uri = self.namespace[entity.replace(" ", "_")]
        query = f"""
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?unitSymbol WHERE {{
            <{entity_uri}> rdf:type :MechanicalProperty ;
                            :hasUnits ?unit .
            ?unit :hasAbbreviation ?unitSymbol .
        }}
        """
        try:
            results = self.ontology.query(query)
            combo_box.clear()
            for row in results:
                combo_box.addItem(str(row.unitSymbol).strip())
        except Exception as e:
            print(f"Error populating units for {entity}: {e}")
    
    
        def query_mechanical_properties(self, bar_instance):
            """Query mechanical properties for a specific bar instance."""
            query = f"""
            PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
            SELECT ?property ?name WHERE {{
                :{bar_instance} :hasMechanicalProperty ?property .
                ?property :hasName ?name .
            }}
            """
            mech_properties = {}
            try:
                results = self.ontology.query(query)
                for row in results:
                    mech_properties[row.name] = {"value": 0.0, "unit": None}
            except Exception as e:
                print(f"Error querying mechanical properties for {bar_instance}: {e}")
            return mech_properties

    def update_with_defaults(self, queried_data, bar_instance, category):
        """Update queried data with default values."""
        defaults = DEFAULT_BAR_CONFIG.get(bar_instance, {}).get(category, {})
        for key, value in defaults.items():
            if key in queried_data:
                queried_data[key]["value"] = value.get("value", queried_data[key]["value"])
                queried_data[key]["unit"] = value.get("unit", queried_data[key]["unit"])
            else:
                queried_data[key] = value
