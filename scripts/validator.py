from pyshacl import validate
from rdflib import Graph
from scripts.rdf_wrapper import RDFWrapper  # Assuming this is your custom wrapper class

class ValidateData:
    """
    A class to validate graph data with defined shapes
    """   
    def __init__(self, experiment_graph_path):
        """
        Initialize the ValidateData class with the RDF graph.

        Args:
            experiment_graph_path (str): Path to the RDF file.
        """
        self.file_path = experiment_graph_path
        self.graph = Graph()
        self.graph.parse(self.file_path, format="turtle")
        
    def validate_with_shacl(self, shacl_file_path):
        """
        Validate the RDF graph against a SHACL shapes file.

        Args:
            shacl_file_path (str): Path to the SHACL shapes file.

        Returns:
            dict: Validation results, including conformance, report graph, and validation messages.
        """
        try:
            # Load SHACL shapes graph
            shacl_graph = Graph()
            shacl_graph.parse(shacl_file_path, format="turtle")

            # Perform validation
            conforms, report_graph, report_text = validate(
                data_graph=self.graph,
                shacl_graph=shacl_graph,
                inference="rdfs",  # Use RDFS inference for validation
                debug=False,       # Set to True for detailed debug info
                advanced=True,     # Enable advanced options
                meta_shacl=False,  # Set to True if validating the SHACL file itself
                depth_limit=50  # Increase the depth limit
            )

            # Return validation results
            return {
                "conforms": conforms,
                "report_graph": report_graph,
                "report_text": report_text,
            }
        except Exception as e:
            print(f"Error during SHACL validation: {e}")
            return None
