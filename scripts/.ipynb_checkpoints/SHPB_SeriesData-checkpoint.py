import numpy as np
import pandas as pd
import os, io
from scripts.rdf_wrapper import RDFWrapper
from rdflib import Graph, Namespace, URIRef, Literal
from scipy.integrate import cumulative_trapezoid
import base64

class SeriesData:
    """
    A class to determine series data for Experiment Tests
    """   
  
    def __init__(self, ontology_path, experiment_graph_path):
        """
        Initialize the SignalExractor with the RDF graph.

        Args:
            ontology_path (str): Path to the RDF file.
        """
        self.ontology_path = ontology_path
        self.file_path = experiment_graph_path
        self.experiment = RDFWrapper(self.file_path) 
        
        ##################################################################################
        #### Step 1: Unpack Variables
        ##################################################################################
        self.secondary_data_uri = self.experiment.get_instances_of_class("dynamat:SecondaryData")[0]
        
        print("Fetching Extracted Signals from RDF")
        self.incident_extracted_pulse = self.fetch_extracted_signals("dynamat:IncidentExtractedSignal")
        self.transmitted_extracted_pulse = self.fetch_extracted_signals("dynamat:TransmittedExtractedSignal")
        self.reflected_extracted_pulse = self.fetch_extracted_signals("dynamat:ReflectedExtractedSignal")
        self.time_extracted_pulse = self.fetch_extracted_signals("dynamat:TimeExtractedSignal")

        #### PLace holder for temp signal handler
        if len(self.experiment.get_instances_of_class("dynamat:TemperatureSensorSignal")) > 0 :
            print("No process defined to handle temperature signals yet!.")            
        print("Extracted signals loaded!")

        # Extract Pulse Duration
        self.pulse_properties = self.experiment.get_objects(self.secondary_data_uri, "dynamat:hasPulseProperty")
        for prop in self.pulse_properties:
            if "Pulse_Duration" in prop:
                self.pulse_duration = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0]) # ms
                print(f"Retrieved pulse duration of {self.pulse_duration:.2e} miliseconds")
        
        # Extract Specimen Original Length and Cross Section
        self.specimen_data_uri = self.experiment.get_instances_of_class("dynamat:SHPBSpecimen")[0]
        self.specimen_dimensions = self.experiment.get_objects(self.specimen_data_uri, "dynamat:hasDimension")
        for prop in self.specimen_dimensions:
            if "OriginalLength" in prop:
                self.specimen_length = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0]) # mm
                print(f"Retrieved specimen length of {self.specimen_length:.2e} mm")
            elif "OriginalCrossSectionalArea" in prop:
                self.specimen_cross = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0]) # mm^2
                print(f"Retrieved specimen cross sectional area of {self.specimen_cross:.2e} mm^2")

        # Extract Bar Dimensions and Properties
        self.bar_data_uri = self.experiment.get_instances_of_class("dynamat:Bar")[0] # Incident Bar
        self.bar_dimensions = self.experiment.get_objects(self.bar_data_uri, "dynamat:hasDimension")
        self.bar_properties = self.experiment.get_objects(self.bar_data_uri, "dynamat:hasMechanicalProperty")
        
        for prop in self.bar_dimensions:
            if "OriginalCrossSectionalArea" in prop:
                self.bar_cross = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0]) # mm^2
                print(f"Retrieved bar cross sectional area of {self.bar_cross:.2e} mm^2")
        for prop in self.bar_properties:
            if "Density" in prop:
                self.bar_density = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0]) # kg/mm^3
                print(f"Retrieved bar density of {self.bar_density:.2e} kg/mm^3")
            elif "ElasticModulus" in prop:
                self.bar_elastic_modulus = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0]) # MPa
                print(f"Retrieved bar elastic modulus of {self.bar_elastic_modulus:.2e} MPa")
            elif "WaveSpeed" in prop:
                self.bar_wave_speed = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0]) # ms
                print(f"Retrieved bar wave speed of {self.bar_wave_speed:.2e} m/s")


        ##################################################################################
        #### Step 2: Calculate Average Engineering Strain Rate and Engineering Strain
        ##################################################################################

        self.strain_rate_series = (self.bar_wave_speed / self.specimen_length) * (self.incident_extracted_pulse.iloc[:,0] - self.reflected_extracted_pulse.iloc[:,0] - self.transmitted_extracted_pulse.iloc[:,0]) *1000 # Converts from 1/ms to 1/s
        print(f"Strain rate was determined with a max value of {np.min(self.strain_rate_series):.3f} 1/ms at {self.time_extracted_pulse.iloc[np.argmin(self.strain_rate_series),0]:.3f} ms")

        # Add to RDF Graph
        self.series_data_class = self.experiment.DYNAMAT.SeriesData
        
        series_name_uri = self.experiment.DYNAMAT["EngineeringStrainRate_Series"]
        series_class_uri = self.experiment.DYNAMAT.EngineeringStrainRate      
        series_data = np.array(self.strain_rate_series).astype(np.float32)
        data_size = len(series_data) 
        self.encoding = "base64Binary"  
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Hertz))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Engineering Strain Rate", datatype = self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Engineering Strain Rate determined from pulse strains",
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))
        self.add_instance_data(self.experiment.DYNAMAT.Hertz)

        self.eng_strain_series = (self.bar_wave_speed / self.specimen_length) * cumulative_trapezoid((self.incident_extracted_pulse.iloc[:,0] - self.reflected_extracted_pulse.iloc[:,0] - self.transmitted_extracted_pulse.iloc[:,0]), self.time_extracted_pulse.iloc[:,0], initial= 0)
        print(f"Engineering Strain was determined with a max value of {np.min(self.eng_strain_series):.3f} mm/mm at {self.time_extracted_pulse.iloc[np.argmin(self.eng_strain_series),0]:.3f} ms")

        # Add Engineering Strain 
        series_name_uri = self.experiment.DYNAMAT["EngineeringStrain_Series"] #
        series_class_uri = self.experiment.DYNAMAT.EngineeringStrain   #
        series_data = np.array(self.eng_strain_series).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Unitless)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Engineering Strain", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Engineering Strain determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))
        
        ##################################################################################
        #### Step 4: Calculate True Strain
        ##################################################################################
        self.true_strain_series = np.log(1 + self.eng_strain_series)
        print(f"True Strain was determined with a max value of {np.min(self.true_strain_series):.3f} mm/mm at {self.time_extracted_pulse.iloc[np.argmin(self.true_strain_series),0]:.3f} ms")

        # Add True Strain 
        series_name_uri = self.experiment.DYNAMAT["TrueStrain_Series"] #
        series_class_uri = self.experiment.DYNAMAT.TrueStrain   #
        series_data = np.array(self.true_strain_series).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Unitless)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("True Strain", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("True Strain determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))
           
        ##################################################################################
        #### Step 5: Calculate Engineering Stress at both Specimen Ends
        ##################################################################################

        self.eng_stress_1 = ((self.bar_cross * self.bar_elastic_modulus) / self.specimen_cross) * (self.incident_extracted_pulse.iloc[:,0] + self.reflected_extracted_pulse.iloc[:,0] )
        print(f"Engineering Stress at the Incident / Specimen interphase was determined with a max value of {np.min(self.eng_stress_1):.3f} MPa at {self.time_extracted_pulse.iloc[np.argmin(self.eng_stress_1),0]:.3f} ms")

        # Add Engineering Stress
        series_name_uri = self.experiment.DYNAMAT["EngineeringStress_Series_1"] #
        series_class_uri = self.experiment.DYNAMAT.EngineeringStress   #
        series_data = np.array(self.eng_stress_1).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Megapascal)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Engineering Stress Front", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Engineering Stress at the incident / specimen determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))

        self.eng_stress_2 = ((self.bar_cross * self.bar_elastic_modulus) / self.specimen_cross) * (self.transmitted_extracted_pulse.iloc[:,0])
        print(f"Engineering Stress at the Transmitted / Specimen interphase was determined with a max value of {np.min(self.eng_stress_2):.3f} MPa at {self.time_extracted_pulse.iloc[np.argmin(self.eng_stress_2),0]:.3f} ms")

        # Add Engineering Stress
        series_name_uri = self.experiment.DYNAMAT["EngineeringStress_Series_2"] #
        series_class_uri = self.experiment.DYNAMAT.EngineeringStress   #
        series_data = np.array(self.eng_stress_2).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Megapascal)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Engineering Stress Back", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Engineering Stress at the transmitted / specimen determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))

        ##################################################################################
        #### Step 6: Calculate True Stress at both Specimen Ends
        ##################################################################################
        
        self.true_stress_1 = self.eng_stress_1 * (1 + self.eng_strain_series)
        print(f"True Stress at the Incident / Specimen interphase was determined with a max value of {np.min(self.true_stress_1):.3f} MPa at {self.time_extracted_pulse.iloc[np.argmin(self.true_stress_1),0]:.3f} ms")

        # Add Engineering Stress
        series_name_uri = self.experiment.DYNAMAT["TrueStress_Series_1"] #
        series_class_uri = self.experiment.DYNAMAT.TrueStress   #
        series_data = np.array(self.true_stress_1).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Megapascal)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("True Stress Front", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("True Stress at the incident / specimen determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))

        self.true_stress_2 = self.eng_stress_2 * (1 + self.eng_strain_series)
        print(f"True Stress at the Transmitted / Specimen interphase was determined with a max value of {np.min(self.true_stress_2):.3f} MPa at {self.time_extracted_pulse.iloc[np.argmin(self.true_stress_2),0]:.3f} ms")

        # Add True Stress 2
        series_name_uri = self.experiment.DYNAMAT["TrueStress_Series_2"] #
        series_class_uri = self.experiment.DYNAMAT.TrueStress   #
        series_data = np.array(self.true_stress_2).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Megapascal)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("True Stress Back", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("True Stress at the transmitted / specimen determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))
        
        ##################################################################################
        #### Step 7: Calculate Pulse's True Strains
        ##################################################################################

        self.incident_true_strain = np.log(1 + self.incident_extracted_pulse.iloc[:,0])
        print(f"True Incident Strain was determined with a max value of {np.min(self.incident_true_strain):.3f} mm/mm at {self.time_extracted_pulse.iloc[np.argmin(self.incident_true_strain),0]:.3f} ms")

        self.reflected_true_strain = np.log(1 + self.reflected_extracted_pulse.iloc[:,0])
        print(f"True Reflected Strain was determined with a max value of {np.max(self.reflected_true_strain):.3f} mm/mm at {self.time_extracted_pulse.iloc[np.argmax(self.reflected_true_strain),0]:.3f} ms")

        self.transmitted_true_strain = np.log(1 + self.transmitted_extracted_pulse.iloc[:,0])
        print(f"True Transmitted Strain was determined with a max value of {np.min(self.transmitted_true_strain):.3f} mm/mm at {self.time_extracted_pulse.iloc[np.argmin(self.transmitted_true_strain),0]:.3f} ms")
        
        ##################################################################################
        #### Step 6: Calculate Pulse's Strain Energies
        ##################################################################################
        
        self.incident_strain_energy = 0.5 * self.bar_cross * self.bar_wave_speed * self.bar_elastic_modulus * self.pulse_duration * (self.incident_true_strain**2)
        print(f"Incident Strain Energy was determined with a max value of {np.max(self.incident_strain_energy):.3f} mJ at {self.time_extracted_pulse.iloc[np.argmax(self.incident_strain_energy),0]:.3f} ms")

        # Add Incident Strain Energy
        series_name_uri = self.experiment.DYNAMAT["Incident_StrainEnergy_Series"] #
        series_class_uri = self.experiment.DYNAMAT.StrainEnergy   #
        series_data = np.array(self.incident_strain_energy).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Millijoule)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Incident Pulse Strain Energy", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Incident Pulse Strain Energy determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))
        
        self.reflected_strain_energy = 0.5 * self.bar_cross * self.bar_wave_speed * self.bar_elastic_modulus * self.pulse_duration * (self.reflected_true_strain**2)
        print(f"Reflected Strain Energy was determined with a max value of {np.max(self.reflected_strain_energy):.3f} mJ at {self.time_extracted_pulse.iloc[np.argmax(self.reflected_strain_energy),0]:.3f} ms")

        # Add Incident Strain Energy
        series_name_uri = self.experiment.DYNAMAT["Reflected_StrainEnergy_Series"] #
        series_class_uri = self.experiment.DYNAMAT.StrainEnergy   #
        series_data = np.array(self.reflected_strain_energy).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Millijoule)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Reflected Pulse Strain Energy", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Reflected Pulse Strain Energy determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))

        self.transmitted_strain_energy = 0.5 * self.bar_cross * self.bar_wave_speed * self.bar_elastic_modulus * self.pulse_duration * (self.transmitted_true_strain**2)
        print(f"Transmitted Strain Energy was determined with a max value of {np.max(self.transmitted_strain_energy):.3f} mJ at {self.time_extracted_pulse.iloc[np.argmax(self.transmitted_strain_energy),0]:.3f} ms")

        # Add Transmitted Strain Energy
        series_name_uri = self.experiment.DYNAMAT["Transmitted_StrainEnergy_Series"] #
        series_class_uri = self.experiment.DYNAMAT.StrainEnergy   #
        series_data = np.array(self.transmitted_strain_energy).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Millijoule)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Transmitted Pulse Strain Energy", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Transmitted Pulse Strain Energy determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))
                
        ##################################################################################
        #### Step 5: Calculate Absorbed Energy
        ##################################################################################
        
        self.delta_e_energy = 0.5 * self.bar_cross * self.bar_wave_speed * self.bar_elastic_modulus * self.pulse_duration * (self.incident_extracted_pulse.iloc[:,0] **2 - self.reflected_extracted_pulse.iloc[:,0]**2 - self.transmitted_extracted_pulse.iloc[:,0]**2) 
        print(f"Spcimen Absorbed Elastic Strain Energy was determined with a max value of {np.max(self.delta_e_energy):.3f} mJ at {self.time_extracted_pulse.iloc[np.argmax(self.delta_e_energy),0]:.3f} ms")

        # Add Transmitted Strain Energy
        series_name_uri = self.experiment.DYNAMAT["Delta_E_Series"] #
        series_class_uri = self.experiment.DYNAMAT.AbsorbedEnergy   #
        series_data = np.array(self.delta_e_energy).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Millijoule)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Absorbed Elastic Energy", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Absorbed Elastic Energy determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))
        self.add_instance_data(self.experiment.DYNAMAT.Millijoule)
        
        self.delta_k_energy = 0.5 *1000 * self.bar_cross * (self.bar_wave_speed**3) * self.bar_density * self.pulse_duration * (self.incident_extracted_pulse.iloc[:,0]**2 - self.reflected_extracted_pulse.iloc[:,0]**2 - self.transmitted_extracted_pulse.iloc[:,0]**2) 
        print(f"Spcimen Absorbed Kinetic Strain Energy was determined with a max value of {np.max(self.delta_k_energy):.3f} mJ at {self.time_extracted_pulse.iloc[np.argmax(self.delta_k_energy),0]:.3f} ms")

        # Add Delta K absorbed Energy
        series_name_uri = self.experiment.DYNAMAT["Delta_K_Series"] #
        series_class_uri = self.experiment.DYNAMAT.AbsorbedEnergy   #
        series_data = np.array(self.delta_k_energy).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Millijoule)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Absorbed Kinetic Energy", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Absorbed Kinetic Energy determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))
        
        self.total_energy = self.delta_e_energy + self.delta_k_energy
        print(f"Total Spcimen Absorbed Strain Energy was determined with a max value of {np.max(self.total_energy):.3f} mJ at {self.time_extracted_pulse.iloc[np.argmax(self.total_energy),0]:.3f} ms")

        # Add Total Strain Energy
        series_name_uri = self.experiment.DYNAMAT["Total_Energy_Series"] #
        series_class_uri = self.experiment.DYNAMAT.AbsorbedEnergy   #
        series_data = np.array(self.total_energy).astype(np.float32) #
        data_size = len(series_data) 
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Millijoule)) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Total Absorbed Energy", datatype = self.experiment.XSD.string))) #
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Total Absorbed Energy determined from pulse strains", #
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(series_name_uri)))

        print("Saving graph to file...")
        print(f"Graph contains: {self.experiment.len()} triples.")
        with open("data/data_out_converter_003.ttl", "w") as f:
            f.write(self.experiment.serialize("turtle"))
    
    def fetch_extracted_signals(self, extracted_signal_class):
        """
        Retrieves all instances for a given class as a pandas DataFrame.
        
        Args:
            extracted_signal_class (str): The class of gauge sensors to fetch signals for.
        
        Returns:
            pd.DataFrame: A DataFrame where each column represents a signal with the column name as the gauge sensor name.
        """
        
        # Initialize an empty DataFrame to store signals
        signals_df = pd.DataFrame()
    
        # Retrieve all sensor instances of the given class
        sensor_data_instances = self.experiment.get_instances_of_class(extracted_signal_class)
    
        for sensor_name in sensor_data_instances:
            # Fetch relevant properties for the sensor
            signal_data = self.experiment.get_objects(sensor_name, "dynamat:hasEncodedData")[0]
            signal_encoding = self.experiment.get_objects(sensor_name, "dynamat:hasEncoding")[0]
            signal_size = int(self.experiment.get_objects(sensor_name, "dynamat:hasSize")[0])
            signal_units = self.experiment.get_objects(sensor_name, "dynamat:hasUnits")[0]
    
            try:
                if signal_encoding == "base64Binary":
                    # Decode the base64 string into bytes
                    signal_data_decoded = base64.b64decode(signal_data)
                    
                    # Convert the bytes to a NumPy array of float32
                    signal_data_decoded = np.frombuffer(signal_data_decoded, dtype=np.float32) 
                    
                    # Ensure the size matches the expected size
                    if len(signal_data_decoded) != signal_size:
                        raise ValueError(f"Decoded data size ({len(signal_data_decoded)}) does not match expected size ({signal_size}).")
                   
                    # Add the signal to the DataFrame with the sensor name as the column header
                    signals_df[sensor_name] = signal_data_decoded
                    print(f"Extracted signal for {sensor_name} loaded...")
                
            except Exception as e:
                print(f"Error processing {sensor_name}: {e}")
    
        return signals_df

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
                        self.experiment.add((URIRef(instance), self.experiment.RDF.type, class_uri))
                        
                    self.experiment.add((URIRef(instance), URIRef(property_uri), Literal(value, datatype=self.experiment.XSD.string)))
            else:
                print(f"No properties found for instance: {instance}")
    
        except Exception as e:
            print(f"Error executing query: {e}")
