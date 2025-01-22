from rdflib import Graph
from pyshacl import validate

def validate_graph(data_graph_path, shapes_graph_path):
    """
    Validate an RDF data graph against a SHACL shapes graph.
    
    Parameters:
        data_graph_path (str): Path to the RDF data graph file (Turtle format).
        shapes_graph_path (str): Path to the SHACL shapes graph file (Turtle format).
    
    Returns:
        dict: Validation results, including conformance and violations.
    """
    # Load the RDF data graph
    data_graph = Graph()
    data_graph.parse(data_graph_path, format="turtle")

    # Load the SHACL shapes graph
    shapes_graph = Graph()
    shapes_graph.parse(shapes_graph_path, format="turtle")

    # Validate the graph
    conforms, report_graph, report_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",  # Enable RDFS reasoning, if required
        debug=True
    )

    # Return validation results
    return {
        "conforms": conforms,
        "report_text": report_text,
        "report_graph": report_graph.serialize(format="turtle")
    }

# Example usage
if __name__ == "__main__":
    data_graph_path = "GUI/experiment_temp.ttl"
    shapes_graph_path = "ontology/DynaMat_SHPB_SHACL.ttl"
    
    validation_results = validate_graph(data_graph_path, shapes_graph_path)
    #print("Conforms:", validation_results["conforms"])
    print("Validation Report:")
    #print(validation_results["report_text"])
    
    # Save the validation report graph to a file (optional)
    with open("validation_report.ttl", "w") as f:
        f.write(validation_results["report_graph"])
