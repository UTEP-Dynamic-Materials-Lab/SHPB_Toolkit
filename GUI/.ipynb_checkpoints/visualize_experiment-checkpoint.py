from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHBoxLayout
from rdflib import Graph
import os

class AddVisualizeWindow(QWidget):
    def __init__(self, ontology_path, database_folder):
        super().__init__()
        self.setWindowTitle("Query Experiments")
        self.database_folder = database_folder

        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")

        # UI elements
        self.layout = QVBoxLayout()
        self.combo_boxes = {}
        self.results_table = QTableWidget(0, 1)
        self.results_table.setHorizontalHeaderLabels(["Matching Files"])

        # Add selection boxes
        for field in ["User", "TestType", "Material"]:
            self.add_selection_box(field)

        # Add search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_database)
        self.layout.addWidget(self.search_button)

        # Add results table
        self.layout.addWidget(self.results_table)
        self.setLayout(self.layout)

        # Populate selection boxes
        self.populate_selection_boxes()

    def add_selection_box(self, field):
        label = QLabel(field)
        combo_box = QComboBox()
        self.combo_boxes[field] = combo_box
        row_layout = QHBoxLayout()
        row_layout.addWidget(label)
        row_layout.addWidget(combo_box)
        self.layout.addLayout(row_layout)

    def populate_selection_boxes(self):
        """
        Populate selection boxes for 'User', 'TestType', and 'Material' based on the ontology.
        """
        queries = {
            "User": """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?user WHERE {
                ?user rdf:type :User .
            }
            """,
            "TestType": """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?testType WHERE {
                ?testType rdf:type :TestType .
            }
            """,
            "Material": """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT DISTINCT ?material WHERE {
                ?material rdf:type :Material .
            }
            """
        }
    
        # Populate combo boxes
        for field, query in queries.items():
            try:
                results = self.ontology.query(query)
                for row in results:
                    value = str(row[0])
                    self.combo_boxes[field].addItem(value)
            except Exception as e:
                print(f"Error populating {field} combo box: {e}")
    
    
    def search_database(self):
        """
        Perform a query across RDF files in the database folder based on user selections.
        """
        # Get user selections
        selected_user = self.combo_boxes["User"].currentText()
        selected_test_type = self.combo_boxes["TestType"].currentText()
        selected_material = self.combo_boxes["Material"].currentText()
    
        # SPARQL query template
        query_template = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        ASK WHERE {{
            ?experiment :hasMetadata ?metadata .
            ?metadata :hasUser <{selected_user}> ;
                      :hasTestingConditions ?conditions .
            ?conditions :hasTestType <{selected_test_type}> .
            ?metadata :hasSpecimen ?specimen .
            ?specimen :hasMaterial <{selected_material}> .
        }}
        """
    
        # Search the folder for matching RDF files
        matches = []
        for file_name in os.listdir(self.database_folder):
            if file_name.endswith(".ttl"):
                file_path = os.path.join(self.database_folder, file_name)
                graph = Graph()
                graph.parse(file_path, format="turtle")
                if graph.query(query_template):
                    matches.append(file_name)
    
        # Update the table with results
        self.update_results_table(matches)
    
    
    def update_results_table(self, matches):
        """
        Populate the results table with matching files.
        """
        self.results_table.setRowCount(len(matches))
        for row, file_name in enumerate(matches):
            self.results_table.setItem(row, 0, QTableWidgetItem(file_name))



