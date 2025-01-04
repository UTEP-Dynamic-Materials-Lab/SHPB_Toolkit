from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QSpinBox, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import QDate
from GUI.components.common_widgets import UserSelector, MaterialSelector, TestTypeSelector, EnvironmentSelector, TestConditionSelector

class TestDescriptionWidget(QWidget):
    def __init__(self, ontology_path, test_config):
        super().__init__()
        self.setWindowTitle("Test Description")
        self.setGeometry(100, 100, 600, 450)

        self.ontology_path = ontology_path
        self.test_config = test_config

        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        # Test Name Display
        test_name_label = QLabel("Generated Test Name:")
        self.test_name_display = QLineEdit()
        self.test_name_display.setReadOnly(True)
        self.layout.addWidget(test_name_label)
        self.layout.addWidget(self.test_name_display)

        # Add User Selector
        self.user_selector = UserSelector(self.ontology_path, self.test_config)
        self.user_selector.user_changed.connect(self.update_test_name)
        self.layout.addWidget(self.user_selector)

        # Add Date Input
        date_label = QLabel("Test Date:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())  # Set to current date by default
        self.date_input.dateChanged.connect(self.update_test_name) 
        self.layout.addWidget(date_label)
        self.layout.addWidget(self.date_input)
        
        # Add Test Condition Selector
        self.test_condition_selector = TestConditionSelector(self.test_config)
        self.test_condition_selector.condition_changed.connect(self.update_test_condition) 
        self.layout.addWidget(self.test_condition_selector)

        # Add Material Selector
        self.material_selector = MaterialSelector(self.ontology_path, self.test_config)
        self.material_selector.material_changed.connect(self.update_test_name)
        self.layout.addWidget(self.material_selector)

        # Add Test Type Selector
        self.test_type_selector = TestTypeSelector(self.test_config)
        self.test_type_selector.test_type_changed.connect(self.update_test_name)
        self.layout.addWidget(self.test_type_selector)

        # Add Environment Selector
        self.environment_selector = EnvironmentSelector(self.test_config)
        self.environment_selector.environment_changed.connect(self.update_environment)
        self.layout.addWidget(self.environment_selector)

        # Experiment ID
        exp_id_label = QLabel("Experiment ID:")
        self.exp_id_spinbox = QSpinBox()
        self.exp_id_spinbox.setRange(1, 999)
        self.exp_id_spinbox.setValue(1)
        self.exp_id_spinbox.valueChanged.connect(self.update_test_name)
        self.layout.addWidget(exp_id_label)
        self.layout.addWidget(self.exp_id_spinbox)

        # Confirm/Edit Button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.toggle_confirm_edit)
        self.layout.addWidget(self.confirm_button)

    def toggle_confirm_edit(self):
        """Toggle between Confirm and Edit modes."""
        editable = self.confirm_button.text() == "Edit"
        self.user_selector.setEnabled(editable)
        self.date_input.setEnabled(editable)
        self.material_selector.setEnabled(editable)
        self.test_type_selector.setEnabled(editable)
        self.environment_selector.setEnabled(editable)
        self.exp_id_spinbox.setEnabled(editable)

        self.confirm_button.setText("Confirm" if editable else "Edit")

    def update_test_name(self):
        """Update the test name dynamically."""
        user_abbreviation = self.test_config.user
        date = self.date_input.date().toString("yyyyMMdd")
        material_abbreviation = self.test_config.specimen_material or "PULSE"
        lab_fea = "LAB" if not self.test_config.is_fea else "FEA"
        ht_rt = self.test_config.environment
        experiment_id = f"{self.exp_id_spinbox.value():03}"

        if user_abbreviation and material_abbreviation:
            test_name = f"{user_abbreviation}_{date}_{material_abbreviation}_{lab_fea}_{ht_rt}_{experiment_id}"
            self.test_name_display.setText(test_name)
        else:
            self.test_name_display.setText("Incomplete Input: Please fill all fields")

    def update_test_condition(self, condition):
        """Handle updates to the test condition."""
        self.test_config.test_condition = condition
        if condition == "Pulse":
            self.material_selector.setEnabled(False)
            self.material_selector.material_combo.setCurrentIndex(-1)  # Clear material selection
        else:
            self.material_selector.setEnabled(True)
        self.update_test_name()  # Ensure the test name reflects the condition

    def update_environment(self, environment):
        """Update environment."""
        self.test_config.environment = environment
        self.update_test_name()

