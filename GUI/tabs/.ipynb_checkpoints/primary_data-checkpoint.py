from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox, QHBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt
from rdflib import Graph, Namespace
import pandas as pd

class PrimaryDataWidget(QWidget):
    def __init__(self, ontology_path, test_config):
        super().__init__()
        self.ontology_path = ontology_path
        self.test_config = test_config

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.signal_spinboxes = {}  # Store spinboxes for signal counts
        self.file_headers = []  # Store file headers
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        # Add signal count fields
        signal_label = QLabel("Define Number of Signals for Each Sensor:")
        self.layout.addWidget(signal_label)
        self.add_signal_count_fields()

        # File upload button
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_button)

        # Table for previewing file contents
        self.table = QTableWidget()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.layout.addWidget(self.table)

        # Mapping section
        mapping_label = QLabel("Map File Columns to Sensor Signals:")
        self.layout.addWidget(mapping_label)
        self.mapping_layout = QVBoxLayout()
        self.layout.addLayout(self.mapping_layout)

    def add_signal_count_fields(self):
        """Add fields for specifying the number of signals for each sensor."""
        query = """
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?sensor ?legendName WHERE {
            ?sensor rdf:type :SensorSignal ;
                    :hasLegendName ?legendName .
        }
        """
        results = self.ontology.query(query)
        for row in results:
            sensor = str(row.sensor)
            legend_name = str(row.legendName)

            # Layout for each sensor
            sensor_layout = QHBoxLayout()
            sensor_label = QLabel(f"{legend_name}:")
            spinbox = QSpinBox()
            spinbox.setRange(0, 10)  # Adjust range as needed

            sensor_layout.addWidget(sensor_label)
            sensor_layout.addWidget(spinbox)
            self.layout.addLayout(sensor_layout)

            # Store spinbox reference
            self.signal_spinboxes[sensor] = spinbox

    def upload_file(self):
        """Handle file upload and render its contents."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", "", "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                # Attempt to auto-detect delimiter
                with open(file_path, 'r') as file:
                    sample = file.read(1024)  # Read a small chunk of the file for delimiter detection
                delimiter = ","  # Default to comma
                if "\t" in sample:
                    delimiter = "\t"  # Tab-separated
                elif ";" in sample:
                    delimiter = ";"  # Semicolon-separated
    
                # Read the file with detected delimiter
                self.file_data = pd.read_csv(file_path, delimiter=delimiter)
                self.file_headers = list(self.file_data.columns)
                print(f"File headers: {self.file_headers}")  # Debugging output for headers
                self.render_file_preview()
    
                # Generate mapping fields based on the uploaded file
                self.generate_mapping_fields()
            except Exception as e:
                print(f"Error reading file: {e}")

    def render_file_preview(self):
        """Display the first few rows of the uploaded file in a table."""
        self.table.setColumnCount(len(self.file_headers))
        self.table.setHorizontalHeaderLabels(self.file_headers)
        preview_data = self.file_data.head().values

        self.table.setRowCount(len(preview_data))
        for row_idx, row_data in enumerate(preview_data):
            for col_idx, cell_data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))

    def generate_mapping_fields(self):
        """Create dropdowns for mapping file columns to signals."""
        # Clear previous mappings
        while self.mapping_layout.count():
            item = self.mapping_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
            if layout := item.layout():
                while layout.count():
                    sub_item = layout.takeAt(0)
                    if sub_widget := sub_item.widget():
                        sub_widget.deleteLater()
                    if sub_layout := sub_item.layout():
                        sub_layout.deleteLater()

        # Generate fields for each signal
        for signal_instance, spinbox in self.signal_spinboxes.items():
            signal_count = spinbox.value()
            if signal_count > 0:
                # Label for the signal
                signal_name = self.signal_name(signal_instance)
                signal_label = QLabel(f"{signal_name}:")
        
                # ComboBox for column mapping
                column_combo = QComboBox()
                column_combo.addItems(["Select a Column"] + self.file_headers)
        
                # ComboBox for units
                unit_combo = QComboBox()
                self.populate_units(signal_instance, unit_combo)
        
                # Layout for the signal mapping
                field_layout = QHBoxLayout()
                field_layout.addWidget(signal_label)
                field_layout.addWidget(column_combo)
                field_layout.addWidget(unit_combo)
    
                self.mapping_layout.addLayout(field_layout)

    def signal_name(self, signal_instance):
        """Retrieve the legend name (hasLegendName) for a given sensor signal instance."""
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?legendName WHERE {{
            <{signal_instance}> :hasLegendName ?legendName .
        }}
        """
        try:
            results = self.ontology.query(query)
            for row in results:
                return str(row.legendName)  # Return the first result's legend name
            print(f"No legend name found for signal instance: {signal_instance}")
            return None
        except Exception as e:
            print(f"Error retrieving legend name for {signal_instance}: {e}")
            return None

    def populate_units(self, signal_instance, unit_combo):
        """Populate unit options for a given signal instance."""
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?unitAbbreviation WHERE {{
            <{signal_instance}> :hasUnits ?unit .
            ?unit :hasAbbreviation ?unitAbbreviation .
        }}
        """
        try:
            results = self.ontology.query(query)
            unit_combo.clear()
            for row in results:
                unit_abbreviation = str(row.unitAbbreviation)
                unit_combo.addItem(unit_abbreviation)
        except Exception as e:
            print(f"Error populating units for {signal_instance}: {e}")