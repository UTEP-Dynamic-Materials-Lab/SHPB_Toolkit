from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox, QHBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt
from rdflib import Graph, Namespace
from GUI.components.common_widgets import UnitSelector, DoubleSpinBox
import pandas as pd
import numpy as np
import base64

class PrimaryDataWidget(QWidget):
    def __init__(self, ontology_path, test_config, experiment_temp_file):
        super().__init__()
        self.ontology_path = ontology_path
        self.test_config = test_config
        self.experiment = experiment_temp_file
        self.test_name = self.test_config.test_name

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.signal_spinboxes = {}  # Store spinboxes for signal counts
        self.file_headers = []  # Store file headers
        self.signal_data = {}
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

        # Confirm/Edit Button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.toggle_confirm_edit)
        self.layout.addWidget(self.confirm_button) 

        self.layout.addStretch()

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
            sensor_uri = str(row.sensor)
            legend_name = str(row.legendName)

            # Layout for each sensor
            sensor_layout = QHBoxLayout()
            sensor_label = QLabel(f"{legend_name}:")
            spinbox = QSpinBox()
            spinbox.setRange(0, 100)  # Adjust range as needed

            sensor_layout.addWidget(sensor_label)
            sensor_layout.addWidget(spinbox)
            self.layout.addLayout(sensor_layout)

            # Store spinbox reference
            self.signal_spinboxes[sensor_uri] = spinbox

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
        for signal_instance_uri, spinbox in self.signal_spinboxes.items():
            signal_count = spinbox.value()
            if signal_count > 0:
                for i in range(0, signal_count):
                    # Label for the signal
                    signal_name = self.signal_name(signal_instance_uri)
                    signal_label = QLabel(f"{signal_name} {i}:")
                    signal_name_uri = self.experiment.DYNAMAT[f"{signal_instance_uri.split('#')[-1]}_{i}"]
            
                    # ComboBox for column mapping
                    column_combo = QComboBox()
                    column_combo.addItem("Select a Column", None)  # Add a placeholder item with no associated data
                    for header in self.file_headers:
                        column_combo.addItem(header, header)  # Add each column header as both the display text and associated data

                    # ComboBox for units
                    unit_combo = UnitSelector(self.ontology_path, signal_instance_uri)
            
                    # Layout for the signal mapping
                    field_layout = QHBoxLayout()
                    field_layout.addWidget(signal_label)
                    field_layout.addWidget(column_combo)
                    field_layout.addWidget(unit_combo)
        
                    self.mapping_layout.addLayout(field_layout)
                
                    # Store widget references in bar_properties
                    if signal_name_uri not in self.signal_data:
                        self.signal_data[signal_name_uri] = []
                    
                    self.signal_data[signal_name_uri].append({
                        "signal_instance_uri": signal_instance_uri,
                        "column_box": column_combo,
                        "unit_box": unit_combo
                    })
                

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

    def update_test_name(self, test_name):
        """ Updates the current test name"""
        self.test_name = test_name

    def toggle_confirm_edit(self):
        """Toggle between Confirm and Edit modes."""
        editable = self.confirm_button.text() == "Edit"
        # Toggle all widgets associated with the bar instance
        self.upload_button.setEnabled(editable)
        for signal_name, signal_box in self.signal_spinboxes.items():
            signal_box.setEnabled(editable)
        for signal_name in self.signal_data:
            for boxes in self.signal_data[signal_name]:
                try: 
                    boxes["column_box"].setEnabled(editable)
                    boxes["unit_box"].setEnabled(editable)
                except Exception as e:
                    print(e)

        # Update the button text
        self.confirm_button.setText("Confirm" if editable else "Edit")

        if not editable:
            primary_data_uri = self.experiment.DYNAMAT["Experiment_Primary_Data"]     

            for signal_name_uri, properties in self.signal_data.items():
                for prop in properties: 
                    signal_instance_uri = prop.get("signal_instance_uri")
                    column_name = prop.get("column_box").currentData()
                    encoding = "base64"
                    data_encoded, data_size = self.clean_data(self.file_data, column_name, encoding) 
                    legend_name = f"{signal_name_uri.split('#')[-1]}"
                    unit_box = prop.get("unit_box")
                    units_uri, _ = unit_box.currentData()

                    self.experiment.set_triple(str(signal_name_uri), str(self.experiment.RDF.type),
                                       str(signal_instance_uri))
                    self.experiment.set_triple(str(signal_name_uri), str(self.experiment.DYNAMAT.hasUnits), units_uri)
                    self.experiment.set_triple(str(signal_name_uri), str(self.experiment.DYNAMAT.hasEncodedData), data_encoded)
                    self.experiment.set_triple(str(signal_name_uri), str(self.experiment.DYNAMAT.hasEncoding), encoding)
                    self.experiment.set_triple(str(signal_name_uri), str(self.experiment.DYNAMAT.hasSize), data_size)                    
                    self.experiment.set_triple(str(signal_name_uri), str(self.experiment.DYNAMAT.hasLegendName), legend_name) 
                    self.experiment.set_triple(str(signal_name_uri), str(self.experiment.DYNAMAT.hasDescription),
                                       f"Data for {signal_name_uri.split('#')[-1]}")
                    self.experiment.add_instance_data(units_uri) # Add the units description
                    
                    self.experiment.add_triple(str(primary_data_uri), str(self.experiment.DYNAMAT.hasSensorSignal),
                                       str(signal_name_uri))  
                    
                self.experiment.save()   


    def clean_data(self, file_data, column_name, encoding):
        """
        Clean and process data for a specific column, converting the input data to a pandas DataFrame.
        
        Parameters:
        - file_data: Raw file data to be converted to a pandas DataFrame.
        - column_name: Name of the column to extract.
        - encoding: Encoding method to use (e.g., base64).
        
        Returns:
        - encoded_data: The encoded data for the specified column.
        - data_size: The length of the extracted data.
        """
        try:
            # Convert the file_data into a pandas DataFrame
            if isinstance(file_data, pd.DataFrame):
                data_df = file_data
            elif isinstance(file_data, np.ndarray):
                data_df = pd.DataFrame(file_data)
            elif isinstance(file_data, str):  # Assuming a file path
                data_df = pd.read_csv(file_data)
            else:
                raise TypeError("Unsupported file_data type. Must be a DataFrame, numpy array, or file path.")
    
            # Validate the column name
            if column_name not in data_df.columns:
                raise KeyError(f"Column '{column_name}' not found in the DataFrame.")
    
            # Extract the column as a numpy array
            column_data = np.array(self.file_data[column_name][5:]).astype(np.float32)
    
            # Calculate the length of the data
            data_size = len(column_data)
    
            # Encode the data
            if encoding == "base64":
                encoded_data = base64.b64encode(column_data.tobytes()).decode("utf-8")
            else:
                raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
    
            return encoded_data, data_size
    
        except KeyError as e:
            raise KeyError(f"Column error: {e}")
        except Exception as e:
            raise RuntimeError(f"Error while processing data: {e}")

       