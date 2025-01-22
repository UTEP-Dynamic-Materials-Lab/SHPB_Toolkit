from rdflib import Graph, Namespace, URIRef, Literal
import base64

class RDFWrapper:
    """
    A utility wrapper for RDF graphs to provide minimal nesting
    and direct access to data.
    """
    # Define reusable namespaces
    DYNAMAT = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    XML = Namespace("http://www.w3.org/XML/1998/namespace")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

    def __init__(self, rdf_file_path, rdf_format="turtle"):
        """
        Initialize the RDFWrapper with an RDF file.

        Args:
            rdf_file_path (str): Path to the RDF file.
            rdf_format (str): Format of the RDF file (default: "turtle").
        """
        self.graph = Graph()
        self.graph.parse(rdf_file_path, format=rdf_format)       
        
        # Bind namespaces for easier readability
        self.graph.bind("dynamat", self.DYNAMAT)
        self.graph.bind("owl", self.OWL)
        self.graph.bind("rdf", self.RDF)
        self.graph.bind("xml", self.XML)
        self.graph.bind("xsd", self.XSD)
        self.graph.bind("rdfs", self.RDFS)

    def expand_prefixed_name(self, prefixed_name):
        """
        Expands a prefixed name (e.g., "dynamat:PrimaryData") into a full URI.

        Args:
            prefixed_name (str): The prefixed name to expand.

        Returns:
            str: The full URI for the given prefixed name.
        """
        # If the input is already a URI, return it directly
        if prefixed_name.startswith("http://") or prefixed_name.startswith("https://"):
            return prefixed_name
        try:     
            if ":" in prefixed_name:
                prefix, name = prefixed_name.split(":")
                namespace = self.graph.namespace_manager.store.namespace(prefix)
                if namespace:
                    return str(namespace) + name
                raise ValueError(f"Prefix '{prefix}' is not bound in the RDF graph.")
            return prefixed_name  # Already a full URI
        except ValueError:
            raise ValueError(f"Invalid prefixed name or URI: {prefixed_name}")
            
    def get_instances_of_class(self, class_name):
        """
        Fetch all instances of a given class.

        Args:
            class_name (str): The URI or prefixed name of the class.

        Returns:
            list: A list of URIs representing instances of the class.
        """
        class_uri = URIRef(self.expand_prefixed_name(class_name))
        query = f"""
        PREFIX rdf: <{self.RDF}>
        SELECT ?instance WHERE {{
            ?instance rdf:type <{class_uri}> .
        }}
        """
        return [
            str(row.instance)
            for row in self.graph.query(query)
        ]

    def get_items(self, subject):
        """
        Fetch predicates and their corresponding objects for a subject.

        Args:
            subject (str): The URI or prefixed name of the subject.

        Returns:
            dict: A dictionary where keys are predicates and values are lists of objects.
        """
        subject_uri = URIRef(self.expand_prefixed_name(subject))
        result = {}
        for predicate, obj in self.graph.predicate_objects(subject_uri):
            pred_str = str(predicate)
            obj_value = str(obj) if not isinstance(obj, URIRef) else str(obj)
            result.setdefault(pred_str, []).append(obj_value)
        return result

    def get_objects(self, subject, predicate):
        """
        Fetch all objects for a given subject and predicate.

        Args:
            subject (str): The URI or prefixed name of the subject.
            predicate (str): The URI or prefixed name of the predicate.

        Returns:
            list: A list of objects for the subject and predicate.
        """
        subject_uri = URIRef(self.expand_prefixed_name(subject))
        predicate_uri = URIRef(self.expand_prefixed_name(predicate))
        return [
            str(obj) if not isinstance(obj, URIRef) else str(obj)
            for obj in self.graph.objects(subject_uri, predicate_uri)
        ]
        
    def get_instances_by_type(self, type_name):
        """
        Fetch all instances of a given type.
    
        Args:
            type_name (str): The name of the type, can be prefixed (e.g., "dynamat:PrimaryData").
    
        Returns:
            list: A list of instances of the given type.
        """
        type_uri = self.expand_prefixed_name(type_name) if ":" in type_name else URIRef(type_name)
        query = f"""
        SELECT ?instance WHERE {{
            ?instance rdf:type <{type_uri}> .
        }}
        """
        return [str(row.instance) for row in self.graph.query(query)]

    def query(self, sparql_query):
        """
        Run a SPARQL query on the graph.

        Args:
            sparql_query (str): A SPARQL query string.

        Returns:
            rdflib.plugins.sparql.processor.SPARQLResult: The result of the query.
        """
        try:
            return self.graph.query(sparql_query)
        except Exception as e:
            print(f"Error executing SPARQL query: {e}")
            return None

    def add(self, triple):
        """
        Add a triple to the RDF graph.

        Args:
            triple (tuple): A tuple containing (subject, predicate, object).
        """
        self.graph.add(triple)

    def set(self, triple):
        """
        Set a triple to the RDF graph.

        Args:
            triple (tuple): A tuple containing (subject, predicate, object).
        """
        self.graph.set(triple)
    
    def remove(self, triple):
        """
        Remove a triple from the RDF graph.

        Args:
            triple (tuple): A tuple containing (subject, predicate, object).
        """
        self.graph.remove(triple)

    def len(self):

       return len(self.graph)
    
    def serialize(self, form):
        return self.graph.serialize(format=form)
