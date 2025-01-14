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

    def set_triple(self, subject, predicate, obj):
        """Add or update a triple in the graph."""
        subject_ref = URIRef(subject)
        predicate_ref = URIRef(predicate)
        
        if isinstance(obj, URIRef):
            object_ref = obj        
        elif isinstance(obj, (float, int)):
            # Create a typed literal for numbers
            object_ref = Literal(obj, datatype=XSD.float if isinstance(obj, float) else XSD.integer)
        elif isinstance(obj, str) and (obj.startswith("http://") or obj.startswith("https://")):
            object_ref = URIRef(obj)  # Treat as URIRef
        else:
            object_ref = Literal(obj)
            
        # Add the triple
        #print(f"Setting triple: {subject}, {predicate}, {obj}")
        self.graph.set((subject_ref, predicate_ref, object_ref))
        #self.save()

    def add_triple(self, subject, predicate, obj):
        """Add a triple in the graph."""
        subject_ref = URIRef(subject)
        predicate_ref = URIRef(predicate)
    
        # Determine if the object is a URI or a Literal
        if isinstance(obj, (str, URIRef)) and (obj.startswith("http://") or obj.startswith("https://")):
            object_ref = URIRef(obj)  # Treat as URIRef
        else:
            object_ref = Literal(obj)  # Treat as Literal
    
        # Add the triple (append, do not overwrite)
        #print(f"Adding triple: {subject}, {predicate}, {obj}")
        self.graph.add((subject_ref, predicate_ref, object_ref))
        #self.save()

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
        - instance_uri (str): The URI of the instance to fetch properties for.
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
            # Print the results and add them to the temp file
            if results:
                #print(f"Properties for instance '{instance}':")
                for row in results:                    
                    property_uri = str(row.property)
                    value = str(row.value)
                    #print(f" - {property_uri}: {value}")
                    self.set_triple(str(instance), str(property_uri), str(value))
                    if row.className:
                        property_class = str(row.className)
                        self.set_triple(instance, str(self.RDF.type), str(property_class))                                        
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



