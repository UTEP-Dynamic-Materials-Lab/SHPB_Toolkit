import os
from rdflib import Graph, Namespace, URIRef, Literal, XSD

class ExperimentTempFile:

    # Define reusable namespaces
    DYNAMAT = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    XML = Namespace("http://www.w3.org/XML/1998/namespace")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    
    def __init__(self, file_path, ontology_path):
        """Initialize the ExperimentTempFile class."""
        self.ontology_path = ontology_path
        self.file_path = file_path
        
    def initialize_temp(self):         
        self.graph = Graph()
        # Bind namespaces
        
        self.graph.bind("dynamat", self.DYNAMAT)
        self.graph.bind("owl", self.OWL)
        self.graph.bind("rdf", self.RDF)
        self.graph.bind("xml", self.XML)
        self.graph.bind("xsd", self.XSD)
        self.graph.bind("rdfs", self.RDFS)

        #self.add_classes()
        
        # Load existing file or initialize a new one
        if os.path.exists(self.file_path):
            self.save()
        else:
            self.save()  # Create an empty file

    def set_triple(self, subject, predicate, obj, obj_type=None):
        """Set a triple in the graph.

        Args:
            subject (str): The subject of the triple.
            predicate (str): The predicate of the triple.
            obj (str|float|int): The object of the triple.
            obj_type (str, optional): The datatype or format of the object. Use one of:
            - 'URIRef': Treat the object as a URI reference.
            - 'xsd:integer': Treat the object as an integer.
            - 'xsd:float': Treat the object as a float.
            - 'xsd:string': Treat the object as a string.
            - 'xsd:base64Binary': Treat the object as base64-encoded binary data.
            - None: Infer the type automatically based on Python type.
        """
        subject_ref = URIRef(subject)
        predicate_ref = URIRef(predicate)

        # Determine object type
        try:         
            if obj_type == "float":
                object_ref = Literal(float(obj), datatype=XSD.float)
            elif obj_type == "int":
                object_ref = Literal(int(obj), datatype=XSD.int)
            elif obj_type == "date":
                object_ref = Literal(obj, datatype=XSD.date)
            elif obj_type == "base64Binary":
                # Convert the object to base64 binary if not already in bytes
                if isinstance(obj, bytes):
                    base64_data = base64.b64encode(obj).decode("utf-8")
                elif isinstance(obj, str):  # Assume input is already base64-encoded
                    base64_data = obj
                else:
                    raise ValueError("Object must be bytes or a base64-encoded string for xsd:base64Binary")
                object_ref = Literal(base64_data, datatype=XSD.base64Binary)
            elif obj.startswith(("http://", "https://")):
                object_ref = URIRef(obj) # Treat as URIRef directly
            elif isinstance(obj, URIRef):
                object_ref = obj   
            else:
                object_ref = Literal(obj, datatype=XSD.string)
        except Exception as e:
            print(e)
            raise ValueError("Object must be assigned a valid xsd:DataType")

        # Add or update the triple
        self.graph.set((subject_ref, predicate_ref, object_ref))

    def add_triple(self, subject, predicate, obj, obj_type="URIRef"):
        """Add or update a triple in the graph.

        Args:
            subject (str): The subject of the triple.
            predicate (str): The predicate of the triple.
            obj (str|float|int): The object of the triple.
            obj_type (str|URIRef|None): The datatype URI, URIRef object, or None.
        """
        subject_ref = URIRef(subject)
        predicate_ref = URIRef(predicate)

        # Determine object type
        try:         
            if obj_type == "float":
                object_ref = Literal(float(obj), datatype=XSD.float)
            elif obj_type == "int":
                object_ref = Literal(int(obj), datatype=XSD.int)
            elif obj_type == "date":
                object_ref = Literal(obj, datatype=XSD.date)
            elif obj_type == "base64Binary":
                # Convert the object to base64 binary if not already in bytes
                if isinstance(obj, bytes):
                    base64_data = base64.b64encode(obj).decode("utf-8")
                elif isinstance(obj, str):  # Assume input is already base64-encoded
                    base64_data = obj
                else:
                    raise ValueError("Object must be bytes or a base64-encoded string for xsd:base64Binary")
                object_ref = Literal(base64_data, datatype=XSD.base64Binary)
            elif obj.startswith(("http://", "https://")):
                object_ref = URIRef(obj) # Treat as URIRef directly
            elif isinstance(obj, URIRef):
                object_ref = obj   
            else:
                object_ref = Literal(obj, datatype=XSD.string)
        except Exception as e:
            print(e)
            raise ValueError("Object must be assigned a valid xsd:DataType")

        # Add or update the triple
        self.graph.add((subject_ref, predicate_ref, object_ref))

    def remove_triple(self, subject, predicate=None, obj=None):
        """Remove a triple from the graph."""
        self.graph.remove((URIRef(subject), URIRef(predicate), Literal(obj)))
        #self.save()

    def query_data(self, sparql_query):
        """Run a SPARQL query on the graph."""
        try:
            return self.graph.query(sparql_query)
        except Exception as e:
            print(f"Error running query: {e}")
            return []

    def save(self):
        """Save the current state of the graph to the file."""
        print("Saving graph to file...")
        print(f"Graph contains: {len(self.graph)} triples.")
        with open(self.file_path, "w") as f:
            f.write(self.graph.serialize(format="turtle"))
            
    def clear(self):
        """Clear all triples from the graph."""
        self.graph = Graph()     
        self.graph.bind("dynamat", self.DYNAMAT)
        self.graph.bind("owl", self.OWL)
        self.graph.bind("rdf", self.RDF)
        self.graph.bind("xml", self.XML)
        self.graph.bind("xsd", self.XSD)
        self.graph.bind("rdfs", self.RDFS)
        self.save()

    def add_instance_data(self, instance):
        """
        Recursively fetch and add all data properties for a given instance in the ontology.
    
        Parameters:
        - instance (str): The URI of the instance to fetch properties for.
        """
        try:
            # Load the ontology
            ontology = Graph()
            ontology.parse(self.ontology_path, format="turtle")
            namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")
            
            # Define the query
            query = f"""
               PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
               PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
               SELECT ?property ?value ?className WHERE {{
                   <{instance}> ?property ?value .
                   OPTIONAL {{ <{instance}> rdf:type ?className . }}
               }}
            """
            
            # Execute the query
            results = ontology.query(query)
            
            # Add the results to the graph
            if results:
                for row in results:
                    property_uri = URIRef(row.property)
                    value = str(row.value)
                    if row.className:
                        class_uri = URIRef(row.className)
                        self.add_triple(URIRef(instance), self.RDF.type, class_uri)
                        
                    self.add_triple(str(instance), str(property_uri), value)
                    
 
            else:
                print(f"No properties found for instance: {instance}")
    
        except Exception as e:
            print(f"Error executing query: {e}")

    def add_classes(self):
        """
        Ensure all classes defined in the ontology are added to the graph.
        This function also maintains the class hierarchy by adding rdfs:subClassOf relationships.
        """
        try:
            ontology = Graph()
            ontology.parse(self.ontology_path, format="turtle")
            namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")
            # Query the ontology to find all classes and their subclasses
            query = """
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?className ?subClass WHERE {
                ?class a owl:Class .
                OPTIONAL { ?subClass rdfs:subClassOf ?className . }
            }
            """
            results = ontology.query(query)
    
            for row in results:
                class_uri = str(row.className)
                subclass_uri = str(row.subClass) if row.subClass else None
    
                # Add the class to the graph
                self.graph.add((URIRef(class_uri), self.RDF.type, self.OWL.Class))
    
                # If a subclass relationship exists, add it as well
                if subclass_uri:
                    self.graph.add((URIRef(subclass_uri), self.RDFS.subClassOf, URIRef(class_uri)))
    
            print("All classes and their hierarchy have been ensured in the graph.")
        except Exception as e:
            print(f"Error ensuring classes in the graph: {e}")



