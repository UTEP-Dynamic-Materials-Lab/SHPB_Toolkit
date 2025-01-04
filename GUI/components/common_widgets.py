from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QComboBox, QRadioButton, QButtonGroup
from PyQt6.QtCore import pyqtSignal
from rdflib import Graph, Namespace

class UserSelector(QWidget):
    user_changed = pyqtSignal(str)  # Emit the selected user abbreviation

    def __init__(self, ontology_path, test_config):
        super().__init__()
        self.test_config = test_config

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # User Label
        user_label = QLabel("User:")
        layout.addWidget(user_label)

        # User ComboBox
        self.user_combo = QComboBox()
        self.user_combo.currentIndexChanged.connect(self.update_user)  # Update on selection change
        layout.addWidget(self.user_combo)

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        self.namespace = Namespace("http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#")

        # Populate Users
        self.populate_users()

    def populate_users(self):
        """Populate the combo box with users from the ontology."""
        query = """
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?Name ?abbreviation WHERE {
            ?user a :User ;
                  :hasName ?Name ;
                  :hasAbbreviation ?abbreviation .
        }
        """
        self.user_combo.clear()
        for row in self.ontology.query(query):
            name = str(row.Name)
            abbreviation = str(row.abbreviation)
            self.user_combo.addItem(f"{name} ({abbreviation})", abbreviation)

    def update_user(self):
        """Update the test configuration and emit the selected user."""
        user = self.user_combo.currentData()
        self.test_config.user = user  # Update global state
        self.user_changed.emit(user)  # Notify listeners

class MaterialSelector(QWidget):
    material_changed = pyqtSignal(str)  # Emit the selected material abbreviation

    def __init__(self, ontology_path, test_config):
        super().__init__()
        self.test_config = test_config

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Material Label
        material_label = QLabel("Material:")
        layout.addWidget(material_label)

        # Material ComboBox
        self.material_combo = QComboBox()
        self.material_combo.currentIndexChanged.connect(self.update_material)  # Update on selection change
        layout.addWidget(self.material_combo)

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        self.namespace = Namespace("http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#")

        # Populate Materials
        self.populate_materials()

    def populate_materials(self):
        """Populate the combo box with materials from the ontology."""
        query = """
        PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
        SELECT ?materialName ?abbreviation ?legendName WHERE {
            ?material rdf:type ?class ;
                      :hasName ?materialName ;
                      :hasAbbreviation ?abbreviation ;
                      :hasLegendName ?legendName .
            ?class rdfs:subClassOf :Material .
        }
        """
        self.material_combo.clear()
        for row in self.ontology.query(query):
            material_name = str(row.materialName)
            material_abbreviation = str(row.abbreviation)
            self.material_combo.addItem(f"{material_name} ({material_abbreviation})", material_abbreviation)

    def update_material(self):
        """Update the test configuration and emit the selected material."""
        material = self.material_combo.currentData()
        self.test_config.specimen_material = material  # Update global state
        self.material_changed.emit(material)  # Notify listeners

class TestTypeSelector(QWidget):
    """Reusable widget for selecting Test Type (LAB/FEA)."""
    test_type_changed = pyqtSignal(str)

    def __init__(self, default="LAB"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Label
        label = QLabel("Test Type:")
        self.layout.addWidget(label)

        # Radio buttons
        self.lab_radio = QRadioButton("LAB")
        self.fea_radio = QRadioButton("FEA")
        self.lab_fea_group = QButtonGroup()
        self.lab_fea_group.addButton(self.lab_radio)
        self.lab_fea_group.addButton(self.fea_radio)

        # Default selection
        if default == "LAB":
            self.lab_radio.setChecked(True)
        else:
            self.fea_radio.setChecked(True)

        # Layout
        type_layout = QHBoxLayout()
        type_layout.addWidget(self.lab_radio)
        type_layout.addWidget(self.fea_radio)
        self.layout.addLayout(type_layout)

        # Connect signals
        self.lab_radio.toggled.connect(self.emit_test_type)

    def emit_test_type(self):
        """Emit the selected test type."""
        test_type = "LAB" if self.lab_radio.isChecked() else "FEA"
        self.test_type_changed.emit(test_type)


class EnvironmentSelector(QWidget):
    """Reusable widget for selecting Environment (HT/RT)."""
    environment_changed = pyqtSignal(str)

    def __init__(self, default="RT"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Label
        label = QLabel("Environment:")
        self.layout.addWidget(label)

        # Radio buttons
        self.ht_radio = QRadioButton("HT")
        self.rt_radio = QRadioButton("RT")
        self.ht_rt_group = QButtonGroup()
        self.ht_rt_group.addButton(self.ht_radio)
        self.ht_rt_group.addButton(self.rt_radio)

        # Default selection
        if default == "RT":
            self.rt_radio.setChecked(True)
        else:
            self.ht_radio.setChecked(True)

        # Layout
        env_layout = QHBoxLayout()
        env_layout.addWidget(self.ht_radio)
        env_layout.addWidget(self.rt_radio)
        self.layout.addLayout(env_layout)

        # Connect signals
        self.ht_radio.toggled.connect(self.emit_environment)

    def emit_environment(self):
        """Emit the selected environment."""
        environment = "HT" if self.ht_radio.isChecked() else "RT"
        self.environment_changed.emit(environment)


class TestConditionSelector(QWidget):
    """Reusable widget for selecting Test Condition (Specimen/Pulse)."""
    condition_changed = pyqtSignal(str)

    def __init__(self, default="Specimen"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Label
        label = QLabel("Test Condition:")
        self.layout.addWidget(label)

        # Radio buttons
        self.specimen_radio = QRadioButton("Specimen")
        self.pulse_radio = QRadioButton("Pulse")
        self.test_condition_group = QButtonGroup()
        self.test_condition_group.addButton(self.specimen_radio)
        self.test_condition_group.addButton(self.pulse_radio)

        # Default selection
        if default == "Specimen":
            self.specimen_radio.setChecked(True)
        else:
            self.pulse_radio.setChecked(True)

        # Layout
        condition_layout = QHBoxLayout()
        condition_layout.addWidget(self.specimen_radio)
        condition_layout.addWidget(self.pulse_radio)
        self.layout.addLayout(condition_layout)

        # Connect signals
        self.specimen_radio.toggled.connect(self.emit_condition)

    def emit_condition(self):
        """Emit the selected test condition."""
        condition = "Specimen" if self.specimen_radio.isChecked() else "Pulse"
        self.condition_changed.emit(condition)


class SpinBoxWithUnit(QWidget):
    value_changed = pyqtSignal(float)

    def __init__(self, min_val, max_val, decimals, units):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(min_val, max_val)
        self.spinbox.setDecimals(decimals)
        self.spinbox.valueChanged.connect(self.emit_value_changed)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(units)

        layout.addWidget(self.spinbox)
        layout.addWidget(self.unit_combo)

    def emit_value_changed(self):
        self.value_changed.emit(self.spinbox.value())

    def get_value(self):
        return self.spinbox.value()

    def set_value(self, value):
        self.spinbox.setValue(value)

class RadioButtonGroup(QWidget):
    selection_changed = pyqtSignal(str)

    def __init__(self, options, default=None):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.button_group = QButtonGroup()
        self.radio_buttons = []

        for option in options:
            radio_button = QRadioButton(option)
            if option == default:
                radio_button.setChecked(True)
            radio_button.toggled.connect(self.emit_selection_changed)
            self.button_group.addButton(radio_button)
            self.radio_buttons.append(radio_button)
            layout.addWidget(radio_button)

    def emit_selection_changed(self):
        selected = next((button.text() for button in self.radio_buttons if button.isChecked()), None)
        if selected:
            self.selection_changed.emit(selected)

    def get_selected(self):
        return next((button.text() for button in self.radio_buttons if button.isChecked()), None)
