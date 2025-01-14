from rdflib import Graph, Namespace

def run_query(ontology_path, instance):
    """
    Run a SPARQL query to fetch properties for a given instance and add them to the temp file.
    """
    try:
        # Load the ontology
        ontology = Graph()
        ontology.parse(ontology_path, format="turtle")
        namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")
        
        # Define the query
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        SELECT ?property ?value WHERE {{
            <{instance}> ?property ?value .
        }}
        """

        # Execute the query
        results = ontology.query(query)

        # Print the results and add them to the temp file
        if results:
            print(f"Properties for instance '{instance}':")
            for row in results:
                property_uri = str(row.property)
                value = str(row.value)
                print(f" - {property_uri}: {value}")
                # Add the triple to the temp file
                
        else:
            print(f"No properties found for instance: {instance}")

    except Exception as e:
        print(f"Error executing query: {e}")

if __name__ == "__main__":
    
    # Define the ontology path and instance
    ontology_path = "ontology/DynaMat_SHPB.ttl"  # Update with the correct path to your ontology file
    instance_uri = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#DavidSantacruz"  # Example instance URI
        
    # Run the query
    run_query(ontology_path, instance_uri)
