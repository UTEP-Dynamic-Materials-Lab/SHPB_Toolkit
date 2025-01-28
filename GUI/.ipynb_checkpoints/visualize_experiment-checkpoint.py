from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHBoxLayout, QLineEdit
from PyQt6.QtGui import QFont
from rdflib import Graph
from GUI.tabs.visualization import VisualizationWindow
import os

class AddVisualizeWindow(QWidget):
    def __init__(self, ontology_path, database_folder):
        super().__init__()
        self.setWindowTitle("Explore Experiment Database")
        self.setGeometry(100, 100, 1000, 600)  # Adjust window size if needed

        # Set font for the entire window
        font = QFont("Calibri", 12)
        self.setFont(font)   
        
        self.database_folder = database_folder

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")

        # UI elements
        self.layout = QVBoxLayout()
        # Add selection inputs
        self.min_value_inputs = {}
        self.max_value_inputs = {}
        self.combo_boxes = {}
        
        # Paired layout for fields
        self.paired_layout = QVBoxLayout()
        self.results_table = QTableWidget(0, 0)  # Initially, no columns
        self.results_table.setHorizontalHeaderLabels([])  # Set dynamically later

        # Fields for selection and corresponding headers for the results table
        self.fields = {
            "TestDate": "Test Date",
            "User": "User",
            "TestType": "Test Type",
            "TestMode": "Test Mode",
            "TestTemperature": "Test Temperature",            
            "MomentumTrap": "Momentum Trap",
            "StrikerVelocity": "Striker Velocity (m/s)",  
            "StrikerPressure": "Striker Pressure (MPa)",  
            "StrikerLength": "Striker Length (mm)" ,    
            "Material": "Material",
            "Shape": "Shape",
            "Structure": "Structure",
            "SpecimenProcessing": "Specimen Processing",   
            "Laboratory": "Laboratory",
        }

        # Add fields to the paired layout
        paired_fields = [
            ("TestDate", True),  # Date range
            ("User", False),  
            ("TestType", False),
            ("TestMode", False),
            ("TestTemperature", False),            
            ("MomentumTrap", False),
            ("StrikerVelocity", True),  # Numeric range
            ("StrikerPressure", True),  # Numeric range
            ("StrikerLength", True),  # Numeric range
            ("Material", False),
            ("Shape", False),
            ("Structure", False),
            ("SpecimenProcessing", False),
            ("Laboratory", False),
        ]
        
        # Loop through fields and add either a combo box or range input
        for field, is_range in paired_fields:
            self.add_selection_box(field, is_range=is_range)
        
        # Add paired layout to the main layout
        self.layout.addLayout(self.paired_layout)
        
        # Set column count and headers for the results table
        self.results_table.setColumnCount(len(self.fields) + 1)  # +1 for "File Name"
        self.results_table.setHorizontalHeaderLabels(["Test / File Name"] + list(self.fields.values()))

        # Add search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_database)
        self.layout.addWidget(self.search_button)

        # Add results table
        self.layout.addWidget(self.results_table)
        self.setLayout(self.layout)

        self.visualize_button = QPushButton("Visualize Selected")
        self.visualize_button.setEnabled(False)  # Initially disabled
        self.visualize_button.clicked.connect(self.open_visualization_window)
        self.layout.addWidget(self.visualize_button)
        
    def add_selection_box(self, field, is_range=False):
        """
        Add a selection box or range input dynamically for a given field,
        pairing two fields per row.
        """
        label = QLabel(self.fields[field])
    
        # Create a new horizontal layout if no current row or the row is full
        if not hasattr(self, 'current_row_layout') or self.current_row_layout.count() >= 4:  # 4 widgets = 2 fields
            self.current_row_layout = QHBoxLayout()
            self.paired_layout.addLayout(self.current_row_layout)
    
        if is_range:
            # Create min and max inputs for range fields
            min_input = QLineEdit()
            max_input = QLineEdit()
            min_input.setPlaceholderText(f"Min {self.fields[field]}")
            max_input.setPlaceholderText(f"Max {self.fields[field]}")
    
            # Save min/max inputs in dictionaries for later use
            self.min_value_inputs[field] = min_input
            self.max_value_inputs[field] = max_input
    
            # Add label, min input, and max input to the row layout
            self.current_row_layout.addWidget(label)
            self.current_row_layout.addWidget(min_input)
            self.current_row_layout.addWidget(max_input)
        else:
            # Create a combo box for categorical fields
            combo_box = QComboBox()
            combo_box.addItem("Any", None)  # Default option
            self.combo_boxes[field] = combo_box
    
            # Populate the combo box with data from the ontology
            self.populate_selection_box(field, combo_box)
    
            # Add label and combo box to the row layout
            self.current_row_layout.addWidget(label)
            self.current_row_layout.addWidget(combo_box)
            
    def populate_selection_box(self, field, combo_box):
        """
        Populate selection boxes for 'User', 'TestType', and 'Material' based on the ontology.
        """
        queries = {
            "User": """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?user ?name WHERE {
                ?user rdf:type :User .
                ?user :hasName ?name .
            }
            """,
            "TestType": """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?testType ?name WHERE {
                ?testType rdf:type :TestType .
                ?testType :hasName ?name .
            }
            """,
            "Material": """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?material ?name WHERE {
                ?material rdf:type ?class .
                ?material :hasName ?name .
                ?class rdfs:subClassOf :Material .
            }
            """, 
            "TestMode" : """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?testMode ?name WHERE {
                ?testMode rdf:type :TestMode .
                ?testMode :hasName ?name .
            }
            """, 
            "TestTemperature" : """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?testTemp ?name WHERE {
                ?testTemp rdf:type :TestTemperature .
                ?testTemp :hasName ?name .
            }
            """, 
            "MomentumTrap" : """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?trap ?name WHERE {
                ?trap rdf:type :MomentumTrap .
                ?trap :hasName ?name .
            }
            """, 
            "Shape" : """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?shape ?name WHERE {
                ?shape rdf:type :Shape .
                ?shape :hasName ?name .
            }
            """, 
            "Structure" : """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?structure ?name WHERE {
                ?structure rdf:type :Structure .
                ?structure :hasName ?name .
            }
            """, 
            "SpecimenProcessing" : """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?process ?name WHERE {
                ?process rdf:type :SpecimenProcessing .
                ?process :hasName ?name .
            }
            """, 
            "Laboratory" : """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?lab ?name WHERE {
                ?lab rdf:type :Laboratory .
                ?lab :hasName ?name .
            }
            """, 
        }
    
        # Populate the combo box with the SPARQL query results
        if field in queries:
            try:
                query = queries[field]
                results = self.ontology.query(query)
                for row in results:
                    uri = str(row[0])
                    name = str(row[1])
                    combo_box.addItem(name, uri)
            except Exception as e:
                print(f"Error populating {field} combo box: {e}")
                
    def search_database(self):
        """
        Perform a query across RDF files in the database folder based on user selections.
        """
        try:
            # Step 1: Build query conditions
            condition_str = self.build_conditions()
    
            # Step 2: Search for matching RDF files
            matches = self.search_rdf_files(condition_str)
    
            # Step 3: Collect metadata values from matches
            results = self.collect_metadata(matches)
    
            # Step 4: Update the results table
            self.update_results_table(results)
        except Exception as e:
            print(f"Error in search_database: {e}")
    
    
    def build_conditions(self):
        """
        Build SPARQL query conditions based on user selections.
        """
        try:
            # Define contexts for fields
            testing_conditions_fields = ["TestMode", "TestTemperature", "TestType", "MomentumTrap"]
            metadata_fields = ["Laboratory", "User", "TestDate", "TestName"]
            specimen_fields = ["Material", "Shape", "Structure", "SpecimenProcessing"]
            numeric_fields = ["StrikerVelocity", "StrikerPressure", "StrikerLength"]
    
            conditions = []
    
            # Handle categorical fields (combo boxes)
            for field, combo_box in self.combo_boxes.items():
                selected_value = combo_box.currentText()
                selected_uri = combo_box.currentData()  # Get the URI stored in the combo box
    
                if selected_value != "Any" and selected_uri:
                    if field in specimen_fields:
                        conditions.append(f"?specimen :has{field} <{selected_uri}> .")
                    elif field in testing_conditions_fields:
                        conditions.append(f"?conditions :has{field} <{selected_uri}> .")
                    elif field in metadata_fields:
                        conditions.append(f"?metadata :has{field} <{selected_uri}> .")
    
            # Handle numeric range fields
            for field in numeric_fields:
                min_val = self.min_value_inputs[field].text()  # Get user input for min
                max_val = self.max_value_inputs[field].text()  # Get user input for max
                if min_val and max_val:
                    if field == "StrikerVelocity":
                        conditions.append(f"""
                        ?conditions :hasBar ?bar .
                        ?bar rdf:type :StrikerBar .
                        ?bar :hasDimension ?velocity .
                        ?velocity rdf:type :Velocity .
                        ?velocity :hasValue ?velocityValue .
                        FILTER (?velocityValue >= {min_val} && ?velocityValue <= {max_val})
                        """)
                    elif field == "StrikerPressure":
                        conditions.append(f"""
                        ?conditions :hasBar ?bar .
                        ?bar rdf:type :StrikerBar .
                        ?bar :hasDimension ?pressure .
                        ?pressure rdf:type :Pressure .
                        ?pressure :hasValue ?pressureValue .
                        FILTER (?pressureValue >= {min_val} && ?pressureValue <= {max_val})
                        """)
                    elif field == "StrikerLength":
                        conditions.append(f"""
                        ?conditions :hasBar ?bar .
                        ?bar rdf:type :StrikerBar .
                        ?bar :hasDimension ?length .
                        ?length rdf:type :OriginalLength .
                        ?length :hasValue ?lengthValue .
                        FILTER (?lengthValue >= {min_val} && ?lengthValue <= {max_val})
                        """)
    
            # Handle TestDate range
            min_date = self.min_value_inputs["TestDate"].text()  # Get min date input
            max_date = self.max_value_inputs["TestDate"].text()  # Get max date input
            if min_date and max_date:
                conditions.append(f"""
                ?metadata :hasTestDate ?testDate .
                FILTER (?testDate >= "{min_date}"^^xsd:date && ?testDate <= "{max_date}"^^xsd:date)
                """)
    
            # Add OPTIONAL conditions for fields with "Any" selection
            for field in self.fields.keys():
                if field in numeric_fields or field == "TestDate":
                    # Skip numeric and date fields as they are already handled
                    continue
    
                if field in specimen_fields:
                    conditions.append(f"""
                    OPTIONAL {{
                        ?specimen :has{field} ?{field.lower()} .
                        ?{field.lower()} :hasName ?{field.lower()}Name .
                    }}
                    """)
                elif field in testing_conditions_fields:
                    conditions.append(f"""
                    OPTIONAL {{
                        ?conditions :has{field} ?{field.lower()} .
                        ?{field.lower()} :hasName ?{field.lower()}Name .
                    }}
                    """)
                elif field in metadata_fields:
                    conditions.append(f"""
                    OPTIONAL {{
                        ?metadata :has{field} ?{field.lower()} .
                        ?{field.lower()} :hasName ?{field.lower()}Name .
                    }}
                    """)
    
            # Ensure all contexts are included in the query
            conditions.insert(0, "?metadata :hasTestingConditions ?conditions .")
            conditions.insert(0, "OPTIONAL {{ ?metadata :hasSpecimen ?specimen }} .")
    
            return "\n".join(conditions)
    
        except Exception as e:
            print(f"Error in build_conditions: {e}")
            raise
    
    def search_rdf_files(self, condition_str):
        """
        Search the database folder for RDF files matching the query conditions.
        """
        try:
            query_template = f"""
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            ASK WHERE {{
                ?experiment :hasMetadata ?metadata .
                {condition_str}
            }}
            """
            matches = []
            for file_name in os.listdir(self.database_folder):
                if file_name.endswith(".ttl"):
                    file_path = os.path.join(self.database_folder, file_name)
                    graph = Graph()
                    graph.parse(file_path, format="turtle")
                    if graph.query(query_template):
                        matches.append(file_name)
            return matches
        except Exception as e:
            print(f"Error in search_rdf_files: {e}")
            raise
    
    
    def collect_metadata(self, matches):
        """
        Collect metadata values for each matching RDF file.
        """
        try:
            results = []
    
            for file_name in matches:
                file_path = os.path.join(self.database_folder, file_name)
                graph = Graph()
                graph.parse(file_path, format="turtle")
    
                # Initialize result row with "N/A" defaults
                row_data = {field: "N/A" for field in self.fields}
                row_data["Test / File Name"] = file_name
    
                # -------------------------
                # 1) Build the OPTIONAL blocks for each group
                # -------------------------
                query_fields = ""
    
                # Metadata fields
                for field in ["User", "Laboratory"]:
                    query_fields += f"""
                      OPTIONAL {{
                        ?metadata :has{field} ?{field.lower()} .
                        ?{field.lower()} :hasName ?{field.lower()}Name .
                      }}
                    """
                
                # For literal fields like TestDate and TestName
                for field in ["TestDate"]:
                    query_fields += f"""
                      OPTIONAL {{
                        ?metadata :has{field} ?{field.lower()} .
                        BIND(STR(?{field.lower()}) AS ?{field.lower()}Name)
                      }}
                    """
    
                # For the conditions fields
                for field in ["TestMode", "TestTemperature", "TestType", "MomentumTrap"]:
                    query_fields += f"""
                      OPTIONAL {{
                        ?conditions :has{field} ?{field.lower()} .
                        ?{field.lower()} :hasName ?{field.lower()}Name .
                      }}
                    """
    
                # For the specimen fields
                for field in ["Material", "Shape", "Structure", "SpecimenProcessing"]:
                    if field == "Material":
                        # "Material" is special because your code checks subClassOf :Material
                        query_fields += """
                          OPTIONAL {
                            ?metadata :hasSpecimen ?specimen .
                            ?specimen :hasMaterial ?material .
                            ?material rdf:type :Material .
                            ?material :hasName ?materialName .

                          }
                        """
                    else:
                        query_fields += f"""
                          OPTIONAL {{
                            ?specimen :has{field} ?{field.lower()} .
                            ?{field.lower()} :hasName ?{field.lower()}Name .
                          }}
                        """

                # For numeric fields
                query_fields += """
                OPTIONAL {
                  ?metadata :hasTestDate ?testDate . 
                }
                
                OPTIONAL {
                  ?conditions :hasBar ?bar .
                  ?bar rdf:type :StrikerBar .
                  ?bar :hasDimension ?velocity .
                  ?velocity rdf:type :Velocity .
                  ?velocity :hasValue ?velocityValue .
                }
                OPTIONAL {
                  ?conditions :hasBar ?bar .
                  ?bar rdf:type :StrikerBar .
                  ?bar :hasDimension ?pressure .
                  ?pressure rdf:type :Pressure .
                  ?pressure :hasValue ?pressureValue .
                }
                OPTIONAL {
                  ?conditions :hasBar ?bar .
                  ?bar rdf:type :StrikerBar .
                  ?bar :hasDimension ?length .
                  ?length rdf:type :OriginalLength .
                  ?length :hasValue ?lengthValue .
                }
                """

                # -------------------------
                # 2) Build a SELECT clause with all needed variables in the correct order
                #    matching self.fields
                # -------------------------
                # For each field, use ?{field.lower()}Name, except for Material => ?materialName
                select_vars = " ".join([
                    "?testdateName", "?userName", "?testtypeName",
                    "?testmodeName", "?testtemperatureName", "?momentumtrapName",
                    "?velocityValue", "?pressureValue", "?lengthValue",
                    "?materialName", "?shapeName", "?structureName", "?specimenprocessingName",
                    "?laboratoryName", # New fields
                ])

                # -------------------------
                # 3) Construct the full SPARQL query
                # -------------------------
                query = f"""
                PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
                SELECT {select_vars}
                WHERE {{
                  ?experiment :hasMetadata ?metadata .
                  ?metadata :hasTestingConditions ?conditions .
                  {query_fields}
                }} 
                LIMIT 1
                """  # or remove LIMIT 1 if you want multiple results
    
                # -------------------------
                # 4) Execute the query and populate row_data
                # -------------------------
                try:
                    # If there is at most one result row, we can do a simple loop:
                    for row in graph.query(query):
                        # row is a tuple in the order of your SELECT variables
                        # We iterate over fields in the same order:
                        for idx, field in enumerate(self.fields):
                            if field in ["StrikerVelocity", "StrikerPressure", "StrikerLength"]:
                                row_data[field] = str(row[idx]) if row[idx] else "0.00"
                            else:
                                key = f"{field.lower()}Name" if field != "Material" else "materialName"
                                row_data[field] = str(row[idx]) if row[idx] else "N/A"

                except Exception as e:
                    print(f"Error querying metadata in file {file_name}: {e}")
    
                results.append(row_data)
            return results
    
        except Exception as e:
            print(f"Error in collect_metadata: {e}")
            raise



    def update_results_table(self, results):
        """
        Update the results table with matches and their associated metadata.
        """
        field_names = list(self.fields.values())  # Use human-readable headers
        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(field_names) + 1)  # File Name + fields
        self.results_table.setHorizontalHeaderLabels(["Test / File Name"] + field_names)
    
        for row, result in enumerate(results):
            for col, field in enumerate(["Test / File Name"] + list(self.fields.keys())):
                self.results_table.setItem(row, col, QTableWidgetItem(result[field]))
        
        # Adjust column widths to fit content
        self.results_table.resizeColumnsToContents()
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)  # Allow multiple selections
        self.results_table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def on_selection_changed(self):
        """
        Enable or disable the Visualize button based on the selection.
        """
        selected_items = self.results_table.selectedItems()
        self.visualize_button.setEnabled(len(selected_items) > 0)
        
    def get_selected_file_paths(self):
        """
        Retrieve the file paths of the selected rows in the results table.
        """
        selected_rows = set(index.row() for index in self.results_table.selectionModel().selectedRows())
        file_paths = [os.path.join(self.database_folder, self.results_table.item(row, 0).text()) for row in selected_rows]  
        return file_paths
        
    def open_visualization_window(self):
        """
        Open the visualization window with selected file paths.
        """
        selected_file_paths = self.get_selected_file_paths()
        if selected_file_paths:
            self.visualization_window = VisualizationWindow(selected_file_paths)  # Pass file paths
            self.visualization_window.show()



