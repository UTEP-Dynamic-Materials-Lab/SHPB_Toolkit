from rdflib import Graph, Namespace

# Define the ontology path
ontology_path = "ontology/DynaMat_SHPB.ttl"

from rdflib import Graph, Namespace

# Define the ontology path
ontology_path = "ontology/DynaMat_SHPB.ttl"

def test_query_units():
    """Test querying units and their symbols for all Dimension instances."""
    # Load the ontology
    ontology = Graph()
    ontology.parse(ontology_path, format="turtle")
    namespace = Namespace("http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#")

    print("Querying units for Dimension instances...")

    query = """
    PREFIX : <http://www.semanticweb.org/ecazares3/ontologies/DynaMat_SHPB#>
    SELECT ?dimensionInstance ?unitSymbol WHERE {
        ?dimensionInstance a :Dimension ;
                           :hasUnits ?unit .
        ?unit :hasSymbol ?unitSymbol .
    }
    """
    results = ontology.query(query)

    if results:
        print("Results found:")
        for row in results:
            dimension_instance = row.dimensionInstance.split("#")[-1]
            unit_symbol = row.unitSymbol
            print(f" - Dimension: {dimension_instance}, Unit Symbol: {unit_symbol}")
    else:
        print("No units found for Dimension instances.")

if __name__ == "__main__":
    test_query_units()


if __name__ == "__main__":
    test_query_units()
