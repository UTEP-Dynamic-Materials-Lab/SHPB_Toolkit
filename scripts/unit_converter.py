from rdflib import Graph, Namespace, URIRef, Literal
import numpy as np
import base64

# Target KG, mm, ms, kN, MPa, kN-mm, kg/mm^3 , m/s, 

class SIConverter:
    """
    A class to perform unit conversions to SI units for specific unit classes in the RDF graph.
    """   
    DYNAMAT = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    XML = Namespace("http://www.w3.org/XML/1998/namespace")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    
    def __init__(self, ontology_path, experiment_graph_path):
        """
        Initialize the SIConverter with the RDF graph.

        Args:
            ontology_path (str): Path to the RDF file.
        """
        self.ontology_path = ontology_path
        self.experiment = Graph() 
        self.experiment.bind("dynamat", self.DYNAMAT)
        self.experiment.bind("owl", self.OWL)
        self.experiment.bind("rdf", self.RDF)
        self.experiment.bind("xml", self.XML)
        self.experiment.bind("xsd", self.XSD)
        self.experiment.bind("rdfs", self.RDFS)
        self.experiment.parse(experiment_graph_path, format="turtle")   

        self.convert_length_units()
        self.convert_density_units()
        self.convert_area_units()
        self.convert_pressure_units()
        self.convert_temperature_units()
        self.convert_velocity_units()
        self.convert_time_units()
        self.convert_ElectricResistance_units()
        self.convert_ElectricPotential_units()

        print("Saving graph to file...")
        print(f"Graph contains: {len(self.experiment)} triples.")
        with open("data/data_out_converter.ttl", "w") as f:
            f.write(self.experiment.serialize(format="turtle"))

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
                        self.experiment.add((URIRef(instance), self.RDF.type, class_uri))
                        
                    self.experiment.add((URIRef(instance), URIRef(property_uri), Literal(value, datatype=self.XSD.string)))
            else:
                print(f"No properties found for instance: {instance}")
    
        except Exception as e:
            print(f"Error executing query: {e}")

    def convert_length_units(self):
        """
        Find all instances with units belonging to the LengthUnit class and convert them to millimeters.
        """
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?instance ?unit ?value WHERE {{
            ?instance :hasUnits ?unit ;
                      :hasValue ?value .
            ?unit rdf:type :LengthUnit .
        }}
        """
        try:
            results = self.experiment.query(query)
            
            for row in results:
                instance_uri = str(row.instance)
                unit_uri = str(row.unit)
                value = float(row.value)
                
                # print(f"Converting Instance: {instance_uri}, Unit: {unit_uri}, Value: {value}")
                
                # Conversion logic using the DYNAMAT namespace
                if unit_uri == str(self.DYNAMAT.Meter):
                    converted_value = value * 1000
                elif unit_uri == str(self.DYNAMAT.Micrometer):
                    converted_value = value * 0.001
                elif unit_uri == str(self.DYNAMAT.Inch):
                    converted_value = value * 25.4
                elif unit_uri == str(self.DYNAMAT.Foot):
                    converted_value = value * 304.8   
                elif unit_uri == str(self.DYNAMAT.Millimeter):
                    converted_value = value
                else: 
                    raise ValueError(f"Unsupported unit type: {unit_uri}")
                
                # Log the conversion
                # print(f"Converted Value for {instance_uri}: {converted_value} mm")
                converted_value = np.float32(converted_value)
                
                # Remove the previous unit definition
                self.experiment.remove((URIRef(unit_uri), None, None))
                self.experiment.remove((URIRef(instance_uri), self.DYNAMAT.hasUnits, None))
                
                # Update the graph with the converted value and the new unit
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasValue, Literal(converted_value, datatype=self.XSD.float)))
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasUnits, self.DYNAMAT.Millimeter))
                self.add_instance_data(self.DYNAMAT.Millimeter)
                
        except Exception as e:
            print(f"Error during length unit conversion: {e}")

    def convert_density_units(self):
        """
        Find all instances with units belonging to the LengthUnit class and convert them to millimeters.
        """
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?instance ?unit ?value WHERE {{
            ?instance :hasUnits ?unit ;
                      :hasValue ?value .
            ?unit rdf:type :DensityUnit .
        }}
        """
        try:
            results = self.experiment.query(query)
            
            for row in results:
                instance_uri = str(row.instance)
                unit_uri = str(row.unit)
                value = float(row.value)
                
                #print(f"Converting Instance: {instance_uri}, Unit: {unit_uri}, Value: {value}")
                
                # Conversion logic using the DYNAMAT namespace
                if unit_uri == str(self.DYNAMAT.GramPerCubicMillimeter):
                    converted_value = value * 0.001
                elif unit_uri == str(self.DYNAMAT.KilogramPerCubicMeter):
                    converted_value = value * 1e-9                    
                elif unit_uri == str(self.DYNAMAT.KilogramPerCubicMillimeter):
                    converted_value = value 
                else: 
                    raise ValueError(f"Unsupported unit type: {unit_uri}")
                
                # Log the conversion
                #print(f"Converted Value for {instance_uri}: {converted_value} mm")
                converted_value = np.float32(converted_value)
                
                # Remove the previous unit definition
                self.experiment.remove((URIRef(unit_uri), None, None))
                self.experiment.remove((URIRef(instance_uri), self.DYNAMAT.hasUnits, None))
                
                # Update the graph with the converted value and the new unit
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasValue, Literal(converted_value, datatype=self.XSD.float)))
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasUnits, self.DYNAMAT.KilogramPerCubicMillimeter))
                self.add_instance_data(self.DYNAMAT.KilogramPerCubicMillimeter)
                
        except Exception as e:
            print(f"Error during length unit conversion: {e}")

    def convert_area_units(self):
        """
        Find all instances with units belonging to the LengthUnit class and convert them to millimeters.
        """
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?instance ?unit ?value WHERE {{
            ?instance :hasUnits ?unit ;
                      :hasValue ?value .
            ?unit rdf:type :AreaUnit .
        }}
        """
        try:
            results = self.experiment.query(query)
            
            for row in results:
                instance_uri = str(row.instance)
                unit_uri = str(row.unit)
                value = float(row.value)
                
                #print(f"Converting Instance: {instance_uri}, Unit: {unit_uri}, Value: {value}")
                
                # Conversion logic using the DYNAMAT namespace
                if unit_uri == str(self.DYNAMAT.SquareInches):
                    converted_value = value * 645.16
                elif unit_uri == str(self.DYNAMAT.SquareMeters):
                    converted_value = value * 1e6                  
                elif unit_uri == str(self.DYNAMAT.SquareMilimeters):
                    converted_value = value 
                else: 
                    raise ValueError(f"Unsupported unit type: {unit_uri}")
                
                # Log the conversion
                #print(f"Converted Value for {instance_uri}: {converted_value} mm")
                converted_value = np.float32(converted_value)
                
                # Remove the previous unit definition
                self.experiment.remove((URIRef(unit_uri), None, None))
                self.experiment.remove((URIRef(instance_uri), self.DYNAMAT.hasUnits, None))
                
                # Update the graph with the converted value and the new unit
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasValue, Literal(converted_value, datatype=self.XSD.float)))
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasUnits, self.DYNAMAT.SquareMilimeters))
                self.add_instance_data(self.DYNAMAT.SquareMilimeters)
                
        except Exception as e:
            print(f"Error during length unit conversion: {e}")

    def convert_pressure_units(self):
        """
        Find all instances with units belonging to the LengthUnit class and convert them to millimeters.
        """
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?instance ?unit ?value WHERE {{
            ?instance :hasUnits ?unit ;
                      :hasValue ?value .
            ?unit rdf:type :PressureUnit .
        }}
        """
        try:
            results = self.experiment.query(query)
            
            for row in results:
                instance_uri = str(row.instance)
                unit_uri = str(row.unit)
                value = float(row.value)
                
                #print(f"Converting Instance: {instance_uri}, Unit: {unit_uri}, Value: {value}")
                
                # Conversion logic using the DYNAMAT namespace
                if unit_uri == str(self.DYNAMAT.Psi):
                    converted_value = value * 6.89476e-3
                elif unit_uri == str(self.DYNAMAT.Pascal):
                    converted_value = value * 1e-6                  
                elif unit_uri == str(self.DYNAMAT.Gigapascal):
                    converted_value = value * 1e3
                elif unit_uri == str(self.DYNAMAT.Megapascal):
                    converted_value = value 
                else: 
                    raise ValueError(f"Unsupported unit type: {unit_uri}")
                
                # Log the conversion
                #print(f"Converted Value for {instance_uri}: {converted_value} mm")
                converted_value = np.float32(converted_value)
                
                # Remove the previous unit definition
                self.experiment.remove((URIRef(unit_uri), None, None))
                self.experiment.remove((URIRef(instance_uri), self.DYNAMAT.hasUnits, None))
                
                # Update the graph with the converted value and the new unit
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasValue, Literal(converted_value, datatype=self.XSD.float)))
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasUnits, self.DYNAMAT.Megapascal))
                self.add_instance_data(self.DYNAMAT.Megapascal)
                
        except Exception as e:
            print(f"Error during length unit conversion: {e}")

    def convert_temperature_units(self):
        """
        Find all instances with units belonging to the LengthUnit class and convert them to millimeters.
        """
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?instance ?unit ?value WHERE {{
            ?instance :hasUnits ?unit ;
                      :hasValue ?value .
            ?unit rdf:type :TemperatureUnit .
        }}
        """
        try:
            results = self.experiment.query(query)
            
            for row in results:
                instance_uri = str(row.instance)
                unit_uri = str(row.unit)
                value = float(row.value)
                
               # print(f"Converting Instance: {instance_uri}, Unit: {unit_uri}, Value: {value}")
                
                # Conversion logic using the DYNAMAT namespace
                if unit_uri == str(self.DYNAMAT.DegressFahrenheit):
                    converted_value = (value * 32 - 32) * (5/9) 
                elif unit_uri == str(self.DYNAMAT.DegreesCelsius):
                    converted_value = value 
                else: 
                    raise ValueError(f"Unsupported unit type: {unit_uri}")
                
                # Log the conversion
                #print(f"Converted Value for {instance_uri}: {converted_value}")
                converted_value = np.float32(converted_value)
                
                # Remove the previous unit definition
                self.experiment.remove((URIRef(unit_uri), None, None))
                self.experiment.remove((URIRef(instance_uri), self.DYNAMAT.hasUnits, None))
                
                # Update the graph with the converted value and the new unit
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasValue, Literal(converted_value, datatype=self.XSD.float)))
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasUnits, self.DYNAMAT.DegreesCelsius))
                self.add_instance_data(self.DYNAMAT.DegreesCelsius)
                
        except Exception as e:
            print(f"Error during length unit conversion: {e}")

    def convert_velocity_units(self):
        """
        Find all instances with units belonging to the LengthUnit class and convert them to millimeters.
        """
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?instance ?unit ?value WHERE {{
            ?instance :hasUnits ?unit ;
                      :hasValue ?value .
            ?unit rdf:type :VelocityUnit .
        }}
        """
        try:
            results = self.experiment.query(query)
            
            for row in results:
                instance_uri = str(row.instance)
                unit_uri = str(row.unit)
                value = float(row.value)
                
               # print(f"Converting Instance: {instance_uri}, Unit: {unit_uri}, Value: {value}")
                
                # Conversion logic using the DYNAMAT namespace
                if unit_uri == str(self.DYNAMAT.FootPerSecond):
                    converted_value = value * 0.3048
                elif unit_uri == str(self.DYNAMAT.InchPerSecond):
                    converted_value = value * 0.0254
                elif unit_uri == str(self.DYNAMAT.MillimeterPerSecond):
                    converted_value = value * 0.001
                elif unit_uri == str(self.DYNAMAT.MeterPerSecond):
                    converted_value = value 
                else: 
                    raise ValueError(f"Unsupported unit type: {unit_uri}")
                
                # Log the conversion
                #print(f"Converted Value for {instance_uri}: {converted_value} mm")
                converted_value = np.float32(converted_value)
                
                # Remove the previous unit definition
                self.experiment.remove((URIRef(unit_uri), None, None))
                self.experiment.remove((URIRef(instance_uri), self.DYNAMAT.hasUnits, None))
                
                # Update the graph with the converted value and the new unit
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasValue, Literal(converted_value, datatype=self.XSD.float)))
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasUnits, self.DYNAMAT.MeterPerSecond))
                self.add_instance_data(self.DYNAMAT.MeterPerSecond)
                
        except Exception as e:
            print(f"Error during length unit conversion: {e}")

    def convert_time_units(self):
        """
        Find all instances with units belonging to the LengthUnit class and convert them to millimeters.
        """
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?instance ?unit ?value WHERE {{
            ?instance :hasUnits ?unit ;
                      :hasEncodedData ?value .
            ?unit rdf:type :TimeUnit .
        }}
        """
        try:
            results = self.experiment.query(query)
            
            for row in results:
                instance_uri = str(row.instance)
                unit_uri = str(row.unit)
                value = base64.b64decode(row.value)
                float32_array = np.frombuffer(value, dtype=np.float32)
                
                #print(f"Converting Instance: {instance_uri}, Unit: {unit_uri}, Value: {value}")
                
                # Conversion logic using the DYNAMAT namespace
                if unit_uri == str(self.DYNAMAT.Second):
                    converted_value = float32_array * 1e3
                elif unit_uri == str(self.DYNAMAT.Microsecond):
                    converted_value = float32_array * 0.001
                elif unit_uri == str(self.DYNAMAT.Millisecond):
                    converted_value = float32_array 
                else: 
                    raise ValueError(f"Unsupported unit type: {unit_uri}")
                
                # Log the conversion
                #print(f"Converted Value for {instance_uri}: {converted_value} mm")
                converted_value = converted_value.tobytes()
                base64_encoded_value = base64.b64encode(converted_value).decode("utf-8")
                
                # Remove the previous unit definition
                self.experiment.remove((URIRef(unit_uri), None, None))
                self.experiment.remove((URIRef(instance_uri), self.DYNAMAT.hasUnits, None))
                
                # Update the graph with the converted value and the new unit
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasEncodedData, Literal(base64_encoded_value,
                                                                                          datatype=self.XSD.base64Binary)))
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasUnits, self.DYNAMAT.Millisecond))
                self.add_instance_data(self.DYNAMAT.Millisecond)
                
        except Exception as e:
            print(f"Error during length unit conversion: {e}")

    def convert_ElectricPotential_units(self):
        """
        Find all instances with units belonging to the ElectricPotentialUnit class and convert them to volts.
        Handles both direct numerical values and base64-encoded data.
        """
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?instance ?unit ?value ?encodedData ?encoding WHERE {{
            ?instance :hasUnits ?unit .
            OPTIONAL {{ ?instance :hasValue ?value . }}
            OPTIONAL {{ ?instance :hasEncodedData ?encodedData ;
                        :hasEncoding ?encoding . }}
            ?unit rdf:type :ElectricPotentialUnit .
        }}
        """
        try:
            results = self.experiment.query(query)
    
            for row in results:
                instance_uri = str(row.instance)
                unit_uri = str(row.unit)
                value = row.value
                encoded_data = row.encodedData
                encoding = row.encoding
    
                if value is not None:
                    # Handle direct numeric values
                    value = float(value)
    
                    # Conversion logic
                    if unit_uri == str(self.DYNAMAT.MilliVolts):
                        converted_value = value * 0.001
                    elif unit_uri == str(self.DYNAMAT.Volts):
                        converted_value = value
                    else:
                        raise ValueError(f"Unsupported unit type: {unit_uri}")
    
                    # Format as float32
                    converted_value = np.float32(converted_value)
    
                    # Update the graph
                    self.experiment.remove((URIRef(unit_uri), None, None))
                    self.experiment.remove((URIRef(instance_uri), self.DYNAMAT.hasUnits, None))
                    self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasValue, Literal(converted_value, datatype=self.XSD.float)))
                    self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasUnits, self.DYNAMAT.Volts))
    
                elif encoded_data is not None and encoding == "base64Binary":
                    # Handle base64-encoded data
                    decoded_data = base64.b64decode(encoded_data)
                    signal_data = np.frombuffer(decoded_data, dtype=np.float32)
    
                    # Conversion logic
                    if unit_uri == str(self.DYNAMAT.MilliVolts):
                        converted_signal = signal_data * 0.001
                    elif unit_uri == str(self.DYNAMAT.Volts):
                        converted_signal = signal_data
                    else:
                        raise ValueError(f"Unsupported unit type: {unit_uri}")
    
                    # Encode back to base64 after conversion
                    converted_signal_encoded = base64.b64encode(converted_signal.tobytes()).decode("utf-8")
    
                    # Update the graph
                    self.experiment.remove((URIRef(unit_uri), None, None))
                    self.experiment.remove((URIRef(instance_uri), self.DYNAMAT.hasUnits, None))
                    self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasEncodedData, Literal(converted_signal_encoded, datatype=self.XSD.base64Binary)))
                    self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasUnits, self.DYNAMAT.Volts))
    
                else:
                    raise ValueError(f"Instance {instance_uri} has neither a value nor encoded data.")
    
        except Exception as e:
            print(f"Error during electric potential unit conversion: {e}")

    def convert_ElectricResistance_units(self):
        """
        Find all instances with units belonging to the LengthUnit class and convert them to millimeters.
        """
        query = f"""
        PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?instance ?unit ?value WHERE {{
            ?instance :hasUnits ?unit ;
                      :hasValue ?value .
            ?unit rdf:type :ElectricResistanceUnit .
        }}
        """
        try:
            results = self.experiment.query(query)
            
            for row in results:
                instance_uri = str(row.instance)
                unit_uri = str(row.unit)
                value = float(row.value)
                
               # print(f"Converting Instance: {instance_uri}, Unit: {unit_uri}, Value: {value}")
                
                # Conversion logic using the DYNAMAT namespace
                if unit_uri == str(self.DYNAMAT.MilliOhms):
                    converted_value = value * 0.001
                elif unit_uri == str(self.DYNAMAT.Ohms):
                    converted_value = value 
                else: 
                    raise ValueError(f"Unsupported unit type: {unit_uri}")
                
                # Log the conversion
                #print(f"Converted Value for {instance_uri}: {converted_value} mm")
                converted_value = np.float32(converted_value)
                
                # Remove the previous unit definition
                self.experiment.remove((URIRef(unit_uri), None, None))
                self.experiment.remove((URIRef(instance_uri), self.DYNAMAT.hasUnits, None))
                
                # Update the graph with the converted value and the new unit
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasValue, Literal(converted_value, datatype=self.XSD.float)))
                self.experiment.set((URIRef(instance_uri), self.DYNAMAT.hasUnits, self.DYNAMAT.Ohms))
                self.add_instance_data(self.DYNAMAT.Ohms)
                
        except Exception as e:
            print(f"Error during length unit conversion: {e}")