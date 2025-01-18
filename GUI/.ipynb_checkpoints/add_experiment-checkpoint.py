from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtGui import QFont
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

        # Set font for the entire window
        font = QFont("Calibri", 12)
        self.setFont(font)        

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
        
        # Specimen Metadata Tab      
        self.specimen_tab = SpecimenMetadataWidget(self.ontology_path, self.test_config, self.experiment_temp_file)
        self.test_description_tab.current_test_mode.connect(self.specimen_tab.update_test_mode)
        self.test_description_tab.current_test_type.connect(self.specimen_tab.update_test_type)
        self.test_description_tab.current_specimen_material.connect(self.specimen_tab.update_specimen_material)
        self.tabs.addTab(self.specimen_tab, "Specimen Metadata")         
        
        # Laboratory Metadata Tab
        self.laboratory_tab = LaboratoryWidget(self.ontology_path, self.test_config, self.experiment_temp_file)
        self.test_description_tab.current_test_name.connect(self.laboratory_tab.update_test_name)
        self.tabs.addTab(self.laboratory_tab, "Laboratory")  

        # Add the Primary Data Tab
        self.primary_data_tab = PrimaryDataWidget(self.ontology_path, self.test_config, self.experiment_temp_file)
        self.test_description_tab.current_test_name.connect(self.primary_data_tab.update_test_name)
        self.tabs.addTab(self.primary_data_tab, "Primary Data")
        





        
        
        
        
        
