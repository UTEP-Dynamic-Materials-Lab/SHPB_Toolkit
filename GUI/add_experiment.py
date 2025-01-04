from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from GUI.tabs.test_description import TestDescriptionWidget
from GUI.tabs.striker_conditions import StrikerConditionsWidget
from GUI.tabs.bar_metadata import BarMetadataWidget
from config.test_config import TestConfiguration


class AddExperimentWindow(QWidget):
    def __init__(self, ontology_path, test_config: TestConfiguration):
        super().__init__()
        self.setWindowTitle("Add Experiment Metadata")
        self.setGeometry(100, 100, 800, 600)  # Adjust window size if needed

        self.ontology_path = ontology_path
        self.test_config = test_config

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
        self.test_description_tab = TestDescriptionWidget(self.ontology_path, self.test_config)
        self.tabs.addTab(self.test_description_tab, "Test Description")

        # Striker Conditions Tab
        self.striker_conditions_tab = StrikerConditionsWidget(self.ontology_path, self.test_config)
        self.tabs.addTab(self.striker_conditions_tab, "Striker Conditions")
        
        # Bar Metadata Tab
        self.bar_metadata_tab = BarMetadataWidget(self.ontology_path, self.test_config)
        self.tabs.addTab(self.bar_metadata_tab, "Bar Metadata")
