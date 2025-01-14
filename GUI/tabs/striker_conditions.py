from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QDoubleSpinBox, QComboBox, QRadioButton, QButtonGroup, QPushButton
)
from rdflib import Graph, Namespace
from PyQt6.QtCore import pyqtSignal, Qt
from GUI.components.common_widgets import UnitSelector, DoubleSpinBox, ClassInstanceSelection

class StrikerConditionsWidget(QWidget):
    def __init__(self, ontology_path, test_config, experiment_temp_file):
        super().__init__()
        self.test_config = test_config
        self.experiment = experiment_temp_file        

        self.ontology = Graph()
        self.ontology_path = ontology_path
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_ui()

    #################################################
    ## WIDGETS INITIALIZATION
    #################################################

    def init_ui(self):
        """Initialize UI components."""

        # Striker Velocity
        striker_velocity_label = QLabel("Striker Velocity:")
        striker_velocity_layout = QHBoxLayout()
        self.velocity_uri = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Velocity"
        self.striker_velocity_spinbox = DoubleSpinBox()
        self.striker_velocity_unit_combo = UnitSelector(self.ontology_path, self.velocity_uri)
        striker_velocity_layout.addWidget(self.striker_velocity_spinbox)
        striker_velocity_layout.addWidget(self.striker_velocity_unit_combo)
        self.layout.addWidget(striker_velocity_label)
        self.layout.addLayout(striker_velocity_layout)

        # Striker Pressure
        striker_pressure_label = QLabel("Striker Pressure:")
        striker_pressure_layout = QHBoxLayout()
        self.pressure_uri = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Pressure" 
        self.striker_pressure_spinbox = DoubleSpinBox()        
        self.striker_pressure_unit_combo = UnitSelector(self.ontology_path, self.pressure_uri)
        striker_pressure_layout.addWidget(self.striker_pressure_spinbox)
        striker_pressure_layout.addWidget(self.striker_pressure_unit_combo)
        self.layout.addWidget(striker_pressure_label)
        self.layout.addLayout(striker_pressure_layout)

        # Add Momentum Trap Condition
        trap_condition_label = QLabel("Momentum Trap Condition:")
        self.layout.addWidget(trap_condition_label)
        self.trap_condition_selector = ClassInstanceSelection(self.ontology_path, self.experiment.DYNAMAT.MomentumTrap)
        self.set_defaults(self.test_config.momentum_trap_condition, self.trap_condition_selector)
        self.trap_condition_selector.currentIndexChanged.connect(self.update_trap_condition)        
        self.layout.addWidget(self.trap_condition_selector)

        # Confirm/Edit Button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.toggle_confirm_edit)
        self.layout.addWidget(self.confirm_button)  

    #################################################
    ## DATA CAPTURE AND RDF GENERATION
    #################################################

    def toggle_confirm_edit(self):
        """Toggle between Confirm and Edit modes."""
        self.test_name = self.test_config.test_name
        editable = self.confirm_button.text() == "Edit"
        self.striker_velocity_spinbox.setEnabled(editable)
        self.striker_velocity_unit_combo.setEnabled(editable)
        self.striker_pressure_spinbox.setEnabled(editable)
        self.striker_pressure_unit_combo.setEnabled(editable) 
        self.trap_condition_selector.setEnabled(editable)

        self.confirm_button.setText("Confirm" if editable else "Edit")
        
        # Add data to temp file
        if not editable:
            metadata_uri = self.experiment.DYNAMAT[f"{self.test_name}_Metadata"]
            testing_conditions_uri = self.experiment.DYNAMAT["Testing_Conditions"]
            striker_bar_uri = self.experiment.DYNAMAT["Striker_Bar"]
                        
            # Add Striker Bar
            self.experiment.set_triple(str(striker_bar_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.StrikerBar))
            self.experiment.add_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasBar),
                                       striker_bar_uri)
            
            # Add Striker Velocity
            striker_bar_velocity_uri = self.experiment.DYNAMAT["Striker_Bar_Velocity"]
            striker_velocity_units_uri, _ = self.striker_velocity_unit_combo.currentData()
            striker_velocity_value = float(self.striker_velocity_spinbox.value())
            
            self.experiment.set_triple(str(striker_bar_velocity_uri), str(self.experiment.RDF.type),
                                       str(self.experiment.DYNAMAT.Velocity))
            self.experiment.set_triple(str(striker_bar_velocity_uri), str(self.experiment.DYNAMAT.hasUnits), striker_velocity_units_uri)
            self.experiment.set_triple(str(striker_bar_velocity_uri), str(self.experiment.DYNAMAT.hasValue), striker_velocity_value)
            self.experiment.set_triple(str(striker_bar_velocity_uri), str(self.experiment.DYNAMAT.hasDescription),
                                       "Initial velocity of the striker bar during testing")
            self.experiment.add_instance_data(striker_velocity_units_uri) # Add the units description
            self.experiment.add_triple(str(striker_bar_uri), str(self.experiment.DYNAMAT.hasDimension), striker_bar_velocity_uri)

            # Add Striker Pressure
            striker_bar_pressure_uri = self.experiment.DYNAMAT["Striker_Bar_Pressure"]
            striker_pressure_units_uri, _ = self.striker_pressure_unit_combo.currentData()
            striker_pressure_value = float(self.striker_pressure_spinbox.value())
            
            self.experiment.set_triple(str(striker_bar_pressure_uri), str(self.experiment.RDF.type),
                                       str(self.experiment.DYNAMAT.Pressure))
            self.experiment.set_triple(str(striker_bar_pressure_uri), str(self.experiment.DYNAMAT.hasUnits), striker_pressure_units_uri)
            self.experiment.set_triple(str(striker_bar_pressure_uri), str(self.experiment.DYNAMAT.hasValue), striker_pressure_value)
            self.experiment.set_triple(str(striker_bar_pressure_uri), str(self.experiment.DYNAMAT.hasDescription),
                                       "Initial pressure of the striker bar during testing")
            self.experiment.add_instance_data(striker_pressure_units_uri) # Add the units description
            self.experiment.add_triple(str(striker_bar_uri), str(self.experiment.DYNAMAT.hasDimension), striker_bar_pressure_uri)

            # Add Momentum Trap Condition            
            trap_condition_uri, _ = self.trap_condition_selector.currentData()            
            self.experiment.set_triple(str(trap_condition_uri), str(self.experiment.RDF.type),
                                       str(self.experiment.DYNAMAT.MomentumTrap))
            self.experiment.set_triple(str(self.experiment.DYNAMAT["Momentum_Trap_Condition"]), str(self.experiment.RDF.type),
                                       str(trap_condition_uri))
            self.experiment.set_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasMomentumTrapCondition),
                                       self.experiment.DYNAMAT["Momentum_Trap_Condition"])
            self.experiment.add_instance_data(trap_condition_uri)
                  
    #################################################
    ## MOMENTUM TRAP CONDITION SELECTOR
    #################################################

    def populate_trap_conditions(self):
        trap_box = QComboBox()       
            
        """Populate the combo box with test conditions from the ontology."""
        query = """
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?instance ?Name ?abbreviation WHERE {
            ?instance a :MomentumTrap ;
                    :hasName ?Name ;
                    :hasAbbreviation ?abbreviation .
        }
        """
        trap_box.clear()
        for row in self.ontology.query(query):
            trap_type = str(row.instance)
            name = str(row.Name)
            abbreviation = str(row.abbreviation)
            trap_box.addItem(f"{name}", (trap_type, abbreviation))
                
        return trap_box
    
    def update_trap_condition(self):
        """Update the test configuration and emit the selected momentum trap condition."""
        trap_condition_uri, abbreviation = self.trap_condition_selector.currentData()
        self.test_config.momentum_trap_condition = trap_condition_uri  # Update global state

    #################################################
    ## DEFAULT POPULATION FUNCTIONS
    #################################################
    def set_defaults(self, instance_uri, combo_box):
        """Set the default material based on the full URI."""
        try:
            # Query the ontology to fetch the abbreviation for the given material URI
            query = f"""
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT ?abbreviation WHERE {{
                <{instance_uri}> :hasAbbreviation ?abbreviation .                    
            }}
            """
            results = self.ontology.query(query)            
            abbreviation = None
            for row in results:
                abbreviation = str(row.abbreviation)
                break  # There should be only one result
    
            if abbreviation:
                target_data = (instance_uri, abbreviation)
                index = self.find_matching_index(combo_box, target_data)
                
                if index >= 0:
                    combo_box.setCurrentIndex(index)
                else:
                    print(f"Default '{abbreviation}' not found in combo box.")
            else:
                print(f"No abbreviation found for URI: {instance_uri}")
        except Exception as e:
            print(f"Error setting default for URI {instance_uri}: {e}")

    def find_matching_index(self, combo_box, target_tuple):
        """
        Find the index of the item in the combo box that matches the target tuple.
    
        Args:
            combo_box (QComboBox): The combo box to search.
            target_tuple (tuple): The tuple to match.
    
        Returns:
            int: The index of the matching item, or -1 if not found.
        """
        for index in range(combo_box.count()):
            item_data = combo_box.itemData(index, role=Qt.ItemDataRole.UserRole)
            if item_data == target_tuple:
                return index
        return -1



