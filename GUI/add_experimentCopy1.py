from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QMessageBox, QTabWidget, QSpinBox, QRadioButton,
    QButtonGroup, QDoubleSpinBox, QScrollArea
)

from PyQt6.QtCore import QDate
import sys
from rdflib import Graph, Namespace

class AddExperimentWindow(QWidget):
    def __init__(self, ontology_path):
        super().__init__()
        self.setWindowTitle("Add Experiment Metadata")

        # Set the anchor and window size 
        self.setGeometry(100, 100, 600, 450)  # Pixels Left to Right, Top to Bottom : (Anchor X, Anchor Y, Size in X, Sixe in Y)
        
        self.is_fea = False  # Track whether the test type is FEA

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        self.namespace = Namespace("http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#")

        # Main Layout with Tabs
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.init_landing_page()
        self.init_conditions_page()
        self.init_bar_metadata_page()

        self.setLayout(self.layout)

    def init_landing_page(self):
        # Landing Page Layout
        landing_page = QWidget()
        layout = QVBoxLayout()

        # Test Name (Non-editable)
        self.test_name_label = QLabel("Generated Test Name:")
        self.test_name_display = QLineEdit()
        self.test_name_display.setReadOnly(True)
        layout.addWidget(self.test_name_label)
        layout.addWidget(self.test_name_display)

        # Test Type Selection
        test_type_label = QLabel("Test Type:")
        self.lab_radio = QRadioButton("LAB")
        self.fea_radio = QRadioButton("FEA")
        self.lab_fea_group = QButtonGroup()
        self.lab_fea_group.addButton(self.lab_radio)
        self.lab_fea_group.addButton(self.fea_radio)
        self.lab_radio.setChecked(True)
        layout.addWidget(test_type_label)

        # User Selection
        user_label = QLabel("User:")
        self.user_combo = QComboBox()
        self.populate_users()
        self.user_combo.currentIndexChanged.connect(self.update_test_name)
        layout.addWidget(user_label)
        layout.addWidget(self.user_combo)

        # Date Input
        date_label = QLabel("Test Date:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.dateChanged.connect(self.update_test_name)
        layout.addWidget(date_label)
        layout.addWidget(self.date_input)

        # Material Selection (Disabled for Pulse Test)
        material_label = QLabel("Material:")
        self.material_combo = QComboBox()
        self.populate_materials(self.material_combo)
        self.material_combo.currentIndexChanged.connect(self.update_test_name)
        layout.addWidget(material_label)
        layout.addWidget(self.material_combo)

        # Test Type Selection
        test_type_label = QLabel("Test Type:")
        self.lab_radio = QRadioButton("LAB")
        self.fea_radio = QRadioButton("FEA")
        self.lab_fea_group = QButtonGroup()
        self.lab_fea_group.addButton(self.lab_radio)
        self.lab_fea_group.addButton(self.fea_radio)
        self.lab_radio.setChecked(True)
        self.lab_radio.toggled.connect(self.confirm_fea_mode)  # Dynamically update FEA-specific options
        test_type_layout = QHBoxLayout()
        test_type_layout.addWidget(self.lab_radio)
        test_type_layout.addWidget(self.fea_radio)
        layout.addWidget(test_type_label)
        layout.addLayout(test_type_layout)

        # HT/RT Toggle
        ht_rt_label = QLabel("Environment:")
        self.ht_radio = QRadioButton("HT")
        self.rt_radio = QRadioButton("RT")
        self.ht_rt_group = QButtonGroup()
        self.ht_rt_group.addButton(self.ht_radio)
        self.ht_rt_group.addButton(self.rt_radio)
        self.rt_radio.setChecked(True)
        self.ht_radio.toggled.connect(self.update_test_name)
        ht_rt_layout = QHBoxLayout()
        ht_rt_layout.addWidget(self.ht_radio)
        ht_rt_layout.addWidget(self.rt_radio)
        layout.addWidget(ht_rt_label)
        layout.addLayout(ht_rt_layout)

        # Experiment ID
        exp_id_label = QLabel("Experiment ID:")
        self.exp_id_spinbox = QSpinBox()
        self.exp_id_spinbox.setRange(1, 999)
        self.exp_id_spinbox.setValue(1)
        self.exp_id_spinbox.valueChanged.connect(self.update_test_name)
        layout.addWidget(exp_id_label)
        layout.addWidget(self.exp_id_spinbox)

        # Confirm/Edit Button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.toggle_confirm_edit)
        layout.addWidget(self.confirm_button)

        landing_page.setLayout(layout)
        self.tabs.addTab(landing_page, "Test Name Entry")

    def toggle_confirm_edit(self):
        """Toggle between Confirm and Edit modes."""
        if self.confirm_button.text() == "Confirm":
            # Confirm mode: Disable all inputs
            self.user_combo.setEnabled(False)
            self.date_input.setEnabled(False)
            self.material_combo.setEnabled(False)
            self.lab_radio.setEnabled(False)
            self.fea_radio.setEnabled(False)
            self.ht_radio.setEnabled(False)
            self.rt_radio.setEnabled(False)
            self.exp_id_spinbox.setEnabled(False)
    
            # Change button to Edit
            self.confirm_button.setText("Edit")
        else:
            # Edit mode: Enable all inputs
            self.user_combo.setEnabled(True)
            self.date_input.setEnabled(True)
            self.material_combo.setEnabled(True)
            self.lab_radio.setEnabled(True)
            self.fea_radio.setEnabled(True)
            self.ht_radio.setEnabled(True)
            self.rt_radio.setEnabled(True)
            self.exp_id_spinbox.setEnabled(True)
    
            # Change button to Confirm
            self.confirm_button.setText("Confirm")
        
    def confirm_fea_mode(self):
        """Confirm and set the global FEA state when the confirm button is clicked."""
        self.is_fea = self.fea_radio.isChecked()
        self.refresh_bar_tabs()
    
    def refresh_bar_tabs(self):
        """Refresh the bar tabs to display FEA-specific fields if applicable."""
        for bar_name, widgets in self.bar_tabs.items():
            widgets["fea_layout_widget"].setVisible(self.is_fea)
            if self.is_fea:
                self.populate_strength_models(widgets["strength_model_combo"])
                self.update_fea_parameters(widgets["strength_model_combo"], widgets["fea_parameter_layout"])

    def init_conditions_page(self):
        # Striker and Conditions Page
        conditions_page = QWidget()
        layout = QVBoxLayout()

        # Striker Velocity
        striker_velocity_label = QLabel("Striker Velocity:")
        striker_velocity_layout = QHBoxLayout()
        self.striker_velocity_spinbox = QDoubleSpinBox()
        self.striker_velocity_spinbox.setRange(0.0, 1000.0)
        self.striker_velocity_spinbox.setDecimals(2)
        self.striker_velocity_unit_combo = QComboBox()
        self.striker_velocity_unit_combo.addItems(["m/s"])
        striker_velocity_layout.addWidget(self.striker_velocity_spinbox)
        striker_velocity_layout.addWidget(self.striker_velocity_unit_combo)
        layout.addWidget(striker_velocity_label)
        layout.addLayout(striker_velocity_layout)

        # Striker Pressure
        striker_pressure_label = QLabel("Striker Pressure:")
        striker_pressure_layout = QHBoxLayout()
        self.striker_pressure_spinbox = QDoubleSpinBox()
        self.striker_pressure_spinbox.setRange(0.0, 10000.0)
        self.striker_pressure_spinbox.setDecimals(2)
        self.striker_pressure_unit_combo = QComboBox()
        self.striker_pressure_unit_combo.addItems(["psi"])
        striker_pressure_layout.addWidget(self.striker_pressure_spinbox)
        striker_pressure_layout.addWidget(self.striker_pressure_unit_combo)
        layout.addWidget(striker_pressure_label)
        layout.addLayout(striker_pressure_layout)

        # Momentum Trap State
        momentum_trap_label = QLabel("Momentum Trap State:")
        self.momentum_engaged_radio = QRadioButton("Engaged")
        self.momentum_not_engaged_radio = QRadioButton("Not Engaged")
        self.momentum_group = QButtonGroup()
        self.momentum_group.addButton(self.momentum_engaged_radio)
        self.momentum_group.addButton(self.momentum_not_engaged_radio)
        self.momentum_not_engaged_radio.setChecked(True)
        momentum_trap_layout = QHBoxLayout()
        momentum_trap_layout.addWidget(self.momentum_engaged_radio)
        momentum_trap_layout.addWidget(self.momentum_not_engaged_radio)
        layout.addWidget(momentum_trap_label)
        layout.addLayout(momentum_trap_layout)

        conditions_page.setLayout(layout)
        self.tabs.addTab(conditions_page, "Striker Initial Conditions")

    
    #########################################################
    ### BAR METADATA
    #########################################################
    
    def init_bar_metadata_page(self):
        """Initialize the Bar Metadata tab."""
        self.bar_metadata_page = QTabWidget()
        self.bar_tabs = {}  # Dictionary to store widgets for each bar
    
        # Fetch Bar Instances from Ontology
        bar_instances = self.get_bar_instances()
    
        # Create a tab for each Bar
        for bar_uri, bar_legend_name in bar_instances.items():
            self.add_bar_tab(bar_legend_name)
    
        self.tabs.addTab(self.bar_metadata_page, "Bar Metadata")
    
    def add_bar_tab(self, bar_name):
        """Create and add a tab for a specific bar."""
        bar_tab = QWidget()
        bar_tab_layout = QVBoxLayout()
    
        # Material Selection
        material_layout = QHBoxLayout()
        material_label = QLabel(f"{bar_name} Material:")
        material_combo = QComboBox()
        self.populate_materials(material_combo)
        material_layout.addWidget(material_label)
        material_layout.addWidget(material_combo)
        bar_tab_layout.addLayout(material_layout)
    
        # Length Input
        self.add_input_field(bar_tab_layout, "Length:", ["m", "mm"])
    
        # Cross-section Input
        self.add_input_field(bar_tab_layout, "Cross Section:", ["m^2", "mm^2"])
    
        # Strain Gauge Distance Input
        self.add_input_field(bar_tab_layout, "Strain Gauge Distance:", ["m", "mm"])
    
        # Mechanical Properties Input
        mechanical_properties_label = QLabel("Mechanical Properties:")
        bar_tab_layout.addWidget(mechanical_properties_label)
        self.add_input_field(bar_tab_layout, "Elastic Modulus:", ["MPa", "GPa"])
        self.add_input_field(bar_tab_layout, "Poisson Ratio:", [])
        self.add_input_field(bar_tab_layout, "Density:", ["Kg/m^3", "Kg/mm^3", "g/mm^3"])
    
      # Add FEA-Specific Fields
        fea_layout = QVBoxLayout()
        fea_layout.setContentsMargins(0, 0, 10, 10)
        
        # Strength Model Selector
        strength_model_layout = QHBoxLayout()
        strength_model_label = QLabel("Strength Model:")
        strength_model_combo = QComboBox()
        strength_model_combo.currentIndexChanged.connect(
            lambda: self.update_fea_parameters(strength_model_combo, fea_layout))
        strength_model_layout.addWidget(strength_model_label)
        strength_model_layout.addWidget(strength_model_combo)
        fea_layout.addLayout(strength_model_layout)
        
        # Populate Strength Models from Ontology
        self.populate_strength_models(strength_model_combo)
        
        # Create a container widget for the FEA layout
        fea_layout_widget = QWidget()
        fea_layout_widget.setLayout(fea_layout)
        fea_layout_widget.setVisible(self.is_fea)  # Set visibility based on FEA state
        bar_tab_layout.addWidget(fea_layout_widget)
        
        # Add bar widgets to the bar_tabs dictionary
        self.bar_tabs[bar_name] = {
            "material_combo": material_combo,
            "fea_layout_widget": fea_layout_widget,
            "strength_model_combo": strength_model_combo,
            "fea_parameter_layout": fea_layout,
        }
        
        bar_tab.setLayout(bar_tab_layout)
        self.bar_metadata_page.addTab(bar_tab, bar_name)


    def populate_users(self):
        query = """
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?user ?Name ?abbreviation WHERE {
            ?user a :User ;
                  :hasName ?Name ;
                  :hasAbbreviation ?abbreviation .
        }
        """
        for row in self.ontology.query(query):
            self.user_combo.addItem(f"{row.Name} ({row.abbreviation})", row.abbreviation)

    def toggle_material_selection(self):
        """Enable or disable material selection based on test type."""
        if self.pulse_test_radio.isChecked():
            self.material_combo.setEnabled(False)
            self.material_combo.setCurrentIndex(-1)  # Clear selection
        else:
            self.material_combo.setEnabled(True)

    def populate_materials(self, material_combo):
        query = """
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?material ?materialName ?abbreviation WHERE {
            ?material a :Material ;
                      :hasLegendName ?materialName ;
                      :hasAbbreviation ?abbreviation .
        }
        """
        material_combo.clear()  # Clear any existing items
        for row in self.ontology.query(query):
            material_name = str(row.materialName)
            abbreviation = str(row.abbreviation)
            material_combo.addItem(f"{material_name} ({abbreviation})", {"name": material_name, "abbreviation": abbreviation})

    def update_test_name(self):
        """Update the test name dynamically based on input fields."""
        user_abbreviation = self.user_combo.currentData()
        date = self.date_input.date().toString("yyyyMMdd")
        
        # Check if material selection is enabled (for specimen tests) or set to "PULSE" for pulse tests
        if self.material_combo.isEnabled():
            material_data = self.material_combo.currentData()
            material_abbreviation = material_data.get('abbreviation') if material_data else "UNKNOWN"
        else:
            material_abbreviation = "PULSE"
        
        lab_fea = "LAB" if self.lab_radio.isChecked() else "FEA"
        ht_rt = "HT" if self.ht_radio.isChecked() else "RT"
        experiment_id = f"{self.exp_id_spinbox.value():03}"
    
        # Construct the test name only if required fields are populated
        if user_abbreviation and material_abbreviation:
            test_name = f"{user_abbreviation}_{date}_{material_abbreviation}_{lab_fea}_{ht_rt}_{experiment_id}"
            self.test_name_display.setText(test_name)
        else:
            self.test_name_display.setText("Incomplete Input: Please fill all fields")

    def get_bar_instances(self):
        """Fetch Bar class instances from the ontology."""
        query = """
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?bar ?legendName WHERE {
            ?bar a :Bar ;
                 :hasLegendName ?legendName .
        }
        """
        bar_instances = {}
        for row in self.ontology.query(query):
            bar_instances[str(row.bar)] = str(row.legendName)
        return bar_instances
    
    def populate_strength_models(self, combo_box):
        """Populate strength models from the ontology."""
        query = """
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?model ?modelName WHERE {
            ?model a :StrengthModel ;
                   :hasName ?modelName .
        }
        """
        for row in self.ontology.query(query):
            combo_box.addItem(row.modelName, str(row.model))
    
    def update_fea_parameters(self, combo_box, fea_layout):
        """Update the parameters displayed for the selected FEA model."""
        model_uri = combo_box.currentData()
        if not model_uri:
            return
    
        # SPARQL query to fetch parameters
        query = f"""
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?param ?paramName WHERE {{
            <{model_uri}> :hasParameter ?param .
            ?param :hasName ?paramName .
                   
        }}
        """
    
        # Ensure parameter layout exists
        if not hasattr(self, 'parameter_layout'):
            self.parameter_layout = QVBoxLayout()
            self.parameter_widget = QWidget()
            self.parameter_widget.setLayout(self.parameter_layout)
            fea_layout.addWidget(self.parameter_widget)
    
        # Clear existing parameter widgets
        while self.parameter_layout.count():
            child = self.parameter_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
        # Populate parameters dynamically based on ontology query
        for row in self.ontology.query(query):
            param_name = str(row.paramName)
            param_units = str("Test")
    
            # Parameter input with units
            param_layout = QHBoxLayout()
            param_label = QLabel(param_name)
            param_input = QDoubleSpinBox()
            param_input.setRange(0, 100000)  # Adjust range as needed
            param_input.setDecimals(3)
            param_units_combo = QComboBox()
    
            # Assign units from ontology
            unit_set = {
                "Density": ["Kg/m³", "Kg/mm³", "g/mm³"],
                "Elastic Modulus": ["Pa", "MPa", "GPa"],
                "Poisson Ratio": ["None"],  # No units
                "Strength Parameter": ["Unitless"],  # Example for other parameters
            }
    
            if param_name in unit_set:
                param_units_combo.addItems(unit_set[param_name])
            else:
                param_units_combo.addItems(["Pa", "MPa", "GPa"])
    
            param_layout.addWidget(param_label)
            param_layout.addWidget(param_input)
            param_layout.addWidget(param_units_combo)
            self.parameter_layout.addLayout(param_layout)



    def add_input_field(self, parent_layout, label_text, units):
        """Add a labeled input field with optional units."""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        spinbox = QDoubleSpinBox()
        spinbox.setRange(0, 10000)  # Example range
        spinbox.setDecimals(3)
        layout.addWidget(label)
        layout.addWidget(spinbox)
    
        if units:
            unit_combo = QComboBox()
            unit_combo.addItems(units)
            layout.addWidget(unit_combo)
    
        parent_layout.addLayout(layout)





