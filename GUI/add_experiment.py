from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from GUI.tabs.test_description import TestDescriptionWidget
from GUI.tabs.striker_conditions import StrikerConditionsWidget
from GUI.tabs.bar_metadata import BarMetadataWidget
from GUI.tabs.specimen_metadata import SpecimenMetadataWidget
from GUI.tabs.primary_data import PrimaryDataWidget
from GUI.tabs.laboratory import LaboratoryWidget
from config.test_config import TestConfiguration
from GUI.experiment_temp import ExperimentTempFile
import os


class AddExperimentWindow(QWidget):
    def __init__(self, ontology_path, test_config: TestConfiguration):
        super().__init__()
        self.setWindowTitle("Add Experiment Metadata")
        self.setGeometry(100, 100, 800, 600)  # Adjust window size if needed

        self.ontology_path = os.path.join("ontology", "DynaMat_SHPB.ttl")
        self.test_config = test_config        

        # Initialize Experiment Temp File
        self.experiment_temp_file = ExperimentTempFile(os.path.join("GUI", "experiment_temp.ttl"), self.ontology_path)        

        # Main layout for the window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Initialize and add tabs
        self.init_tabs()

    def init_tabs(self):
        """Initialize and add tabs to the TabWidget."""
        # Dynamically handle the pulse test selection
        def handle_pulse_test_change(is_pulse):
            # Remove the Laboratory tab first, if it exists
            lab_tab_index = self.tabs.indexOf(self.laboratory_tab)
            if lab_tab_index != -1:
                self.tabs.removeTab(lab_tab_index)
            
            if is_pulse:
                # Remove the Specimen Metadata tab if it exists
                specimen_tab_index = self.tabs.indexOf(self.specimen_tab)
                if specimen_tab_index != -1:
                    self.tabs.removeTab(specimen_tab_index)
            else:
                # Add the Specimen Metadata tab if it doesn't exist
                if self.tabs.indexOf(self.specimen_tab) == -1:
                    self.tabs.addTab(self.specimen_tab, "Specimen Metadata") 
                                
            # Add the Laboratory tab back as the last tab
            if not hasattr(self, "laboratory_tab"):
                self.laboratory_tab = LaboratoryWidget(self.ontology_path, self.test_config)
            self.tabs.addTab(self.laboratory_tab, "Laboratory")

        # Tab widget for multiple tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Test Description Tab
        self.test_description_tab = TestDescriptionWidget(self.ontology_path, self.test_config, self.experiment_temp_file)
        self.tabs.addTab(self.test_description_tab, "Test Description") 
        
        # Striker Conditions Tab
        self.striker_conditions_tab = StrikerConditionsWidget(self.ontology_path, self.test_config, self.experiment_temp_file)
        self.tabs.addTab(self.striker_conditions_tab, "Striker Conditions")
        
        # Bar Metadata Tab
        self.bar_metadata_tab = BarMetadataWidget(self.ontology_path, self.test_config, self.experiment_temp_file)
        self.test_description_tab.current_test_mode.connect(self.bar_metadata_tab.update_test_mode)
        self.tabs.addTab(self.bar_metadata_tab, "Bar Metadata")
        """
        # Specimen Metadata Tab      
        self.specimen_tab = SpecimenMetadataWidget(self.ontology_path, self.test_config)
        self.test_description_tab.test_type_selector.fea_mode_changed.connect(self.specimen_tab.update_visibility)

        # Laboratory Metadata Tab
        self.laboratory_tab = LaboratoryWidget(self.ontology_path, self.test_config)
        self.tabs.addTab(self.laboratory_tab, "Laboratory")      
                
        # Initial check for the current state of the pulse test
        handle_pulse_test_change(self.test_config.is_pulse)
        self.test_description_tab.test_condition_selector.pulse_test.connect(handle_pulse_test_change)

        # Add the Primary Data Tab
        self.primary_data_tab = PrimaryDataWidget(self.ontology_path, self.test_config)
        self.tabs.addTab(self.primary_data_tab, "Primary Data")
        """





        
        
        
        
        
