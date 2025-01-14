from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QComboBox, QRadioButton, QButtonGroup
from rdflib import Graph, Namespace
from PyQt6.QtCore import Qt

class MaterialSelector(QComboBox): 
    """ Returns a selection box populated with defined material instances"""
    def __init__(self, ontology_path, class_uri, parent=None):
        super().__init__(parent)
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        self.class_uri = class_uri

        self.populate_materials()
    
    def populate_materials(self):
        """Populate the combo box with materials from the ontology."""
        query = """
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?material ?materialName ?abbreviation ?legendName WHERE {
            ?material rdf:type ?class ;
                      :hasName ?materialName ;
                      :hasAbbreviation ?abbreviation ;
                      :hasLegendName ?legendName .
            ?class rdfs:subClassOf :Material .
        }
        """
        self.clear()
        try:
            for row in self.ontology.query(query):
                material_uri = str(row.material)
                material_name = str(row.materialName)
                material_abbreviation = str(row.abbreviation)
                self.addItem(f"{material_name} ({material_abbreviation})", (material_uri, material_abbreviation))
        except Exception as e:
            print(f"Error populating units for {self.class_uri}: {e}")        

class UnitSelector(QComboBox):
    """ Returns a selection box populated with the property's assigned units"""
    def __init__(self, ontology_path, property_instance_uri, parent=None):
        super().__init__(parent)
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        self.property_instance_uri = property_instance_uri

        # Populate the combo box with units
        self.populate_units()

    def populate_units(self):
        """Populate units for the given property."""
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?unit ?unitAbbreviation WHERE {{
            <{self.property_instance_uri}> :hasUnits ?unit .
            ?unit :hasAbbreviation ?unitAbbreviation .
        }}
        """
        try:
            results = self.ontology.query(query)
            self.clear()
            for row in results:
                unit_uri = str(row.unit)
                unit_abbreviation = str(row.unitAbbreviation)
                self.addItem(unit_abbreviation, (unit_uri, unit_abbreviation))
        except Exception as e:
            print(f"Error populating units for {self.property_instance_uri}: {e}")

class DoubleSpinBox(QDoubleSpinBox):
    """ Creates a Double Spin Box for float data entries"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0.0, 10000.0)
        self.setDecimals(4)
        
class ClassInstanceSelection(QComboBox):
    """Returns a selection box with the name of the class instance"""
    def __init__(self, ontology_path, class_uri, parent=None):
        super().__init__(parent)
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        self.class_uri = class_uri

        self.populate_class_instances()
    
    def populate_class_instances(self):       
            
        """Populate the combo box with test conditions from the ontology."""
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?instance ?Name ?abbreviation WHERE {{
            ?instance a <{self.class_uri}> ;
                        :hasName ?Name ;
                        :hasAbbreviation ?abbreviation .
        }}
        """

        self.clear()
        try: 
            for row in self.ontology.query(query):
                instance_uri = str(row.instance)
                name = str(row.Name)
                abbreviation = str(row.abbreviation)
                self.addItem(f"{name}", (instance_uri, abbreviation))
        except Exception as e:
            print(f"Error populating units for {self.class_uri}: {e}")

class SetDefaults:
    def __init__(self, ontology_path, instance_uri, combo_box):
        self.ontology_path = ontology_path
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")
        self.instance_uri = instance_uri
        self.combo_box = combo_box

        self.set_defaults()        
               
    def set_defaults(self):        
        """Set the default material based on the full URI."""
        try:
            # Query the ontology to fetch the abbreviation for the given material URI
            query = f"""
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT ?abbreviation WHERE {{
                <{self.instance_uri}> :hasAbbreviation ?abbreviation .                    
            }}
            """
            results = self.ontology.query(query)            
            abbreviation = None
            for row in results:
                abbreviation = str(row.abbreviation)
                break  # There should be only one result
    
            if abbreviation:
                target_data = (self.instance_uri, abbreviation)
                index = self.find_matching_index(target_data)
                
                if index >= 0:
                    self.combo_box.setCurrentIndex(index)
                else:
                    print(f"Default '{abbreviation}' not found in combo box.")
            else:
                print(f"No abbreviation found for URI: {self.instance_uri}")
        except Exception as e:
            print(f"Error setting default material for URI {self.instance_uri}: {e}")

    def find_matching_index(self, target_tuple):
        """
        Find the index of the item in the combo box that matches the target tuple.
    
        Args:
            combo_box (QComboBox): The combo box to search.
            target_tuple (tuple): The tuple to match.
    
        Returns:
            int: The index of the matching item, or -1 if not found.
        """
        for index in range(self.combo_box.count()):
            item_data = self.combo_box.itemData(index, role=Qt.ItemDataRole.UserRole)
            if item_data == target_tuple:
                return index
        return -1
    