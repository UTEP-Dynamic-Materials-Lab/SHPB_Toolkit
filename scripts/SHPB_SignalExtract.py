import numpy as np
import pandas as pd
import os, io
from scripts.rdf_wrapper import RDFWrapper
from rdflib import Graph, Namespace, URIRef, Literal
import base64

class SignalExtractor:
    """
    A class to perform pulse signal extraction from the experiment graph
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
        #### Step 1: Fetch Sensor Signals, and variables to perfrom preliminary analysis
        #### This analysis part is common to all valid test conditions entries.
        ##################################################################################
        
        self.incident_sensor_signals = self.fetch_gauge_signals("dynamat:IncidentSensorSignal") # unitless 
        self.transmitted_sensor_signals = self.fetch_gauge_signals("dynamat:TransmittedSensorSignal") # unitless
        self.time_sensor_signals = self.fetch_sensor_signals("dynamat:TimeSensorSignal") # ms       

        ####! Note: Should we include a filled array of same value? or just ommit when used in RT and no temp signal?
        if len(self.experiment.get_instances_of_class("dynamat:TemperatureSensorSignal")) > 0 :
            self.temperature_sensor_signals = self.fetch_sensor_signals("dynamat:TemperatureSensorSignal") # Degrees C
        else: 
            print("No Temperature Sensor Signal Defined.")

        ##################################################################################
        #### Step 2: Fetch or determine Elastic Wave Speeds
        #### For Pulse Tests, determine a new wave speed from the signal
        #### For Specimen Tests, fetches the assigned wave speed values of the bars
        ##################################################################################
        
        # Calculate Wave Speed or use wave speed
        self.testing_conditions_uri = self.experiment.get_instances_of_class("dynamat:TestingConditions")[0]
        self.test_type = self.experiment.get_objects(self.testing_conditions_uri, "dynamat:hasTestType")[0]
        self.wave_speed, self.pulse_speed = self.determine_wave_speed() # mm / ms = m/s  
        
        ###########################################################################################
        #### Step 3: Determine Loading Duration, Stress and Strain Amplitude and Stress Wave Length
        ###########################################################################################
        
        # Retrive striker bar lenght 
        self.striker_bar_uri = self.experiment.get_instances_of_class("dynamat:StrikerBar")[0]
        self.striker_bar_dimensions = self.experiment.get_objects(self.striker_bar_uri, "dynamat:hasDimension")
        self.striker_bar_properties = self.experiment.get_objects(self.striker_bar_uri, "dynamat:hasMechanicalProperty")
        
        for prop in self.striker_bar_dimensions:
            if "OriginalLength" in prop:
                self.striker_length = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0]) # mm
            elif "Velocity" in prop:
                self.striker_velocity = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0]) # m/s
        for prop in self.striker_bar_properties:
            if "Density" in prop:
                self.striker_density = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0]) # kg/mm3
        
        self.pulse_duration = self.determine_pulse_duration(self.striker_length, self.wave_speed) # mm/ms or m/s
        self.incident_stress_pulse = self.determine_incident_stress_pulse(self.striker_density, self.wave_speed,
                                                                          self.striker_velocity) # 
        self.incident_strain_pulse = self.determine_incident_strain_pulse(self.wave_speed, self.striker_velocity)
        self.pulse_length = 2 * self.striker_length
        print(f"Length of Stress Wave : {self.pulse_length:.2e} mm")

        ###########################################################################################
        #### Step 4: Extract Pulse Signals from Sensor Signal
        ###########################################################################################
        
        dt = np.mean(np.diff(self.time_sensor_signals.iloc[:,0])) # Determines Pulse Duration in number of Index Points
        self.pulse_time_points =  int(self.pulse_duration / dt)
        self.inter_variable = 1
        print(f"Number of time points : {self.pulse_time_points} points")
        print(f"Number of interpolation points : {self.inter_variable - 1}")
        
        self.incident_extracted_signals = pd.DataFrame() 
        self.reflected_extracted_signals = pd.DataFrame() 
        self.transmitted_extracted_signals = pd.DataFrame()         

        # Extract Incident and Reflected Signals
        if self.incident_sensor_signals.shape[1] == 1:
            for sensor_signal_idx in range(self.incident_sensor_signals.shape[1]):  # Iterate over columns
                strain_signal = self.incident_sensor_signals.iloc[:, sensor_signal_idx]
                sensor_name = self.incident_sensor_signals.columns[sensor_signal_idx].replace("Sensor", "Extracted")           
                print(f"Processing column {sensor_name}:")
            
                incident_extracted = self.extract_pulse_data(strain_signal, self.pulse_time_points, interpolation = self.inter_variable,
                                                             min_search = True, cutoff = 1e-5, offset = 0)
                self.incident_extracted_signals[sensor_name] = incident_extracted
                reflected_extracted = self.extract_pulse_data(strain_signal, self.pulse_time_points, interpolation = self.inter_variable,
                                                             min_search = False, cutoff = 1e-5, offset = 0)
                sensor_name = self.incident_extracted_signals.columns[sensor_signal_idx].replace("Incident", "Reflected")
                self.reflected_extracted_signals[sensor_name] = reflected_extracted
                print(f"Sucessfully extracted incident and reflected signals from {self.incident_sensor_signals.columns[sensor_signal_idx]} ")
        else :
            raise ValueError(f"Logic not defined for the amount of {self.incident_sensor_signals.shape[1]} Incident Sensor Signals")

        # Extract Transmitted Signals
        if self.transmitted_sensor_signals.shape[1] == 1:
            for sensor_signal_idx in range(self.transmitted_sensor_signals.shape[1]):  # Iterate over columns
                strain_signal = self.transmitted_sensor_signals.iloc[:, sensor_signal_idx]
                sensor_name = self.transmitted_sensor_signals.columns[sensor_signal_idx].replace("Sensor", "Extracted")           
                print(f"Processing column {sensor_name}:")
            
                transmitted_extracted = self.extract_pulse_data(strain_signal, self.pulse_time_points,
                                                                interpolation = self.inter_variable,
                                                                min_search = True, cutoff = 1e-5, offset = 0)
                self.transmitted_extracted_signals[sensor_name] = transmitted_extracted
                print(f"Sucessfully extracted transmitted signals from {self.transmitted_sensor_signals.columns[sensor_signal_idx]} ")
        else :
            raise ValueError(f"Logic not defined for the amount of {self.transmitted_sensor_signals.shape[1]} Transmitted Sensor Signals")

        if len(self.experiment.get_instances_of_class("dynamat:TemperatureSensorSignal")) > 0 :
            if self.temperature_sensor_signals.shape[1] == 1:
                raise ValueError(f"Logic not defined for the amount of {self.temperature_sensor_signals.shape[1]} Temperature Sensor Signals")
                
        new_time_steps = int(self.pulse_time_points * self.inter_variable)
        self.extracted_time = np.linspace(0, dt * (self.pulse_time_points - 1), new_time_steps)
        print(f"Extracted time with {new_time_steps} points, every {dt:.2e} miliseconds")

        ###########################################################################################
        #### Step 5: Save Secondary Data to RDF
        ###########################################################################################
        self.secondary_data_uri = str(self.experiment.DYNAMAT["Experiment_Secondary_Data"])

        # Add Pulse Duration, Length, Speed, and Stress / Strain Amplitudes
        pulse_duration_uri = str(self.experiment.DYNAMAT["Pulse_Duration"])
        self.experiment.add((URIRef(pulse_duration_uri), self.experiment.RDF.type, self.experiment.DYNAMAT.PulseProperties))
        self.experiment.add((URIRef(pulse_duration_uri), self.experiment.RDF.type, self.experiment.DYNAMAT.PulseDuration))
        self.experiment.add((URIRef(pulse_duration_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Millisecond))
        self.experiment.add((URIRef(pulse_duration_uri), self.experiment.DYNAMAT.hasValue,
                             Literal(self.pulse_duration, datatype = self.experiment.XSD.float )))
        self.experiment.add((URIRef(pulse_duration_uri), self.experiment.DYNAMAT.hasDescription, 
                             Literal("Test wave pulse duration", datatype = self.experiment.XSD.string )))
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasPulseProperty, URIRef(pulse_duration_uri)))

        pulse_length_uri = str(self.experiment.DYNAMAT["Pulse_Length"])
        self.experiment.add((URIRef(pulse_length_uri), self.experiment.RDF.type, self.experiment.DYNAMAT.PulseProperties))
        self.experiment.add((URIRef(pulse_length_uri), self.experiment.RDF.type, self.experiment.DYNAMAT.PulseLength))
        self.experiment.add((URIRef(pulse_length_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Millimeter))
        self.experiment.add((URIRef(pulse_length_uri), self.experiment.DYNAMAT.hasValue,
                             Literal(self.pulse_length, datatype = self.experiment.XSD.float )))
        self.experiment.add((URIRef(pulse_length_uri), self.experiment.DYNAMAT.hasDescription, 
                             Literal("Test wave pulse length", datatype = self.experiment.XSD.string )))
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasPulseProperty, URIRef(pulse_length_uri)))

        pulse_speed_uri = str(self.experiment.DYNAMAT["Pulse_Speed"])
        self.experiment.add((URIRef(pulse_speed_uri), self.experiment.RDF.type, self.experiment.DYNAMAT.PulseProperties))
        self.experiment.add((URIRef(pulse_speed_uri), self.experiment.RDF.type, self.experiment.DYNAMAT.PulseSpeed))
        self.experiment.add((URIRef(pulse_speed_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.MeterPerSecond))
        self.experiment.add((URIRef(pulse_speed_uri), self.experiment.DYNAMAT.hasValue,
                             Literal(self.pulse_speed, datatype = self.experiment.XSD.float )))
        self.experiment.add((URIRef(pulse_speed_uri), self.experiment.DYNAMAT.hasDescription, 
                             Literal("Test wave pulse speed", datatype = self.experiment.XSD.string )))
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasPulseProperty, URIRef(pulse_speed_uri)))

        incident_stress_pulse_uri = str(self.experiment.DYNAMAT["Pulse_Stress_Amplitude"])
        self.incident_stress_pulse *= 1000 # Converts it to MPa
        self.experiment.add((URIRef(incident_stress_pulse_uri), self.experiment.RDF.type, self.experiment.DYNAMAT.PulseProperties))
        self.experiment.add((URIRef(incident_stress_pulse_uri), self.experiment.RDF.type, self.experiment.DYNAMAT.PulseStressAmplitude))
        self.experiment.add((URIRef(incident_stress_pulse_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Megapascal))
        self.experiment.add((URIRef(incident_stress_pulse_uri), self.experiment.DYNAMAT.hasValue,
                             Literal(self.incident_stress_pulse, datatype = self.experiment.XSD.float )))
        self.experiment.add((URIRef(incident_stress_pulse_uri), self.experiment.DYNAMAT.hasDescription, 
                             Literal("Test pulse stress amplitude", datatype = self.experiment.XSD.string )))
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasPulseProperty, 
                             URIRef(incident_stress_pulse_uri)))

        incident_strain_pulse_uri = str(self.experiment.DYNAMAT["Pulse_Strain_Amplitude"])
        self.experiment.add((URIRef(incident_strain_pulse_uri), self.experiment.RDF.type, self.experiment.DYNAMAT.PulseProperties))
        self.experiment.add((URIRef(incident_strain_pulse_uri), self.experiment.RDF.type, self.experiment.DYNAMAT.PulseStrainAmplitude))
        self.experiment.add((URIRef(incident_strain_pulse_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Unitless))
        self.experiment.add((URIRef(incident_strain_pulse_uri), self.experiment.DYNAMAT.hasValue,
                             Literal(self.incident_strain_pulse, datatype = self.experiment.XSD.float )))
        self.experiment.add((URIRef(incident_strain_pulse_uri), self.experiment.DYNAMAT.hasDescription, 
                             Literal("Test pulse strain amplitude", datatype = self.experiment.XSD.string )))
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasPulseProperty, 
                             URIRef(incident_strain_pulse_uri)))

        # Save Incident and Reflected Extracted Signals         
        self.incident_sensor_signals_names = self.experiment.get_instances_of_class("dynamat:IncidentSensorSignal")
        if self.incident_extracted_signals.shape[1] == 1:
            for idx, name in enumerate(self.incident_sensor_signals_names): 
                incident_name_uri = name.replace("Sensor", "Extracted") # Extracted Sensor URI
                reflected_name_uri = incident_name_uri.replace("Incident", "Reflected") # Extracted Sensor URI
                extracted_signal_class = self.experiment.DYNAMAT.ExtractedSignal
                incident_signal_class = self.experiment.DYNAMAT.IncidentExtractedSignal
                reflected_signal_class = self.experiment.DYNAMAT.ReflectedExtractedSignal   
    
                incident_data = np.array(self.incident_extracted_signals.iloc[:, idx]).astype(np.float32)
                reflected_data = np.array(self.reflected_extracted_signals.iloc[:, idx]).astype(np.float32)
                data_size = len(incident_data) if len(incident_data) == len(reflected_data) else print("Incident and Reflected Signals do not share the same size")
                encoding = "base64Binary"  
    
                if encoding == "base64Binary":
                    incident_encoded_data = base64.b64encode(incident_data.tobytes()).decode("utf-8")
                    reflected_encoded_data = base64.b64encode(reflected_data.tobytes()).decode("utf-8")
                else:
                    raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
                
                # Add Incident Extracted Signal
                self.experiment.add((URIRef(incident_name_uri), self.experiment.RDF.type, extracted_signal_class))
                self.experiment.add((URIRef(incident_name_uri), self.experiment.RDF.type, incident_signal_class))
                self.experiment.add((URIRef(incident_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Unitless))
                self.experiment.add((URIRef(incident_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                     Literal(incident_encoded_data, datatype = self.experiment.XSD.base64Binary)))
                self.experiment.add((URIRef(incident_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                     Literal(encoding, datatype = self.experiment.XSD.string)))
                self.experiment.add((URIRef(incident_name_uri), self.experiment.DYNAMAT.hasSize,
                                     Literal(data_size, datatype = self.experiment.XSD.int)))
                self.experiment.add((URIRef(incident_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                     Literal("Incident", datatype = self.experiment.XSD.string)))
                self.experiment.add((URIRef(incident_name_uri), self.experiment.DYNAMAT.hasDescription,
                                     Literal("Extracted Incident Signal from SG", datatype = self.experiment.XSD.string)))                
                self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                     URIRef(incident_name_uri)))
                                    
                # Add Reflected Extracted Signal
                self.experiment.add((URIRef(reflected_name_uri), self.experiment.RDF.type, extracted_signal_class))
                self.experiment.add((URIRef(reflected_name_uri), self.experiment.RDF.type, reflected_signal_class))
                self.experiment.add((URIRef(reflected_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Unitless))
                self.experiment.add((URIRef(reflected_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                     Literal(reflected_encoded_data, datatype = self.experiment.XSD.base64Binary)))
                self.experiment.add((URIRef(reflected_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                     Literal(encoding, datatype = self.experiment.XSD.string)))
                self.experiment.add((URIRef(reflected_name_uri), self.experiment.DYNAMAT.hasSize,
                                     Literal(data_size, datatype = self.experiment.XSD.int)))
                self.experiment.add((URIRef(reflected_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                     Literal("Reflected", datatype = self.experiment.XSD.string)))
                self.experiment.add((URIRef(reflected_name_uri), self.experiment.DYNAMAT.hasDescription,
                                     Literal("Extracted Reflected Signal from SG", datatype = self.experiment.XSD.string)))               
                self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                     URIRef(reflected_name_uri)))
        else: 
            raise ValueError(f"Logic not defined for the amount of {self.incident_extracted_signals.shape[1]} Extracted Incident/Refelcted Sensor Signals")

        # Add Extracted Transmitted Data
        self.transmitted_sensor_signals_names = self.experiment.get_instances_of_class("dynamat:TransmittedSensorSignal")
        if self.transmitted_extracted_signals.shape[1] == 1:
            for idx, name in enumerate(self.transmitted_sensor_signals_names): 
                transmitted_name_uri = name.replace("Sensor", "Extracted") # Extracted Sensor URI
                extracted_signal_class = self.experiment.DYNAMAT.ExtractedSignal
                transmitted_signal_class = self.experiment.DYNAMAT.TransmittedExtractedSignal   
    
                transmitted_data = np.array(self.transmitted_extracted_signals.iloc[:, idx]).astype(np.float32)
                data_size = len(transmitted_data) 
                encoding = "base64Binary"  
    
                if encoding == "base64Binary":
                    transmitted_encoded_data = base64.b64encode(transmitted_data.tobytes()).decode("utf-8")
                else:
                    raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
                
                # Add transmitted Extracted Signal
                self.experiment.add((URIRef(transmitted_name_uri), self.experiment.RDF.type, extracted_signal_class))
                self.experiment.add((URIRef(transmitted_name_uri), self.experiment.RDF.type, transmitted_signal_class))
                self.experiment.add((URIRef(transmitted_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Unitless))
                self.experiment.add((URIRef(transmitted_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                     Literal(transmitted_encoded_data, datatype = self.experiment.XSD.base64Binary)))
                self.experiment.add((URIRef(transmitted_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                     Literal(encoding, datatype =  self.experiment.XSD.string)))
                self.experiment.add((URIRef(transmitted_name_uri), self.experiment.DYNAMAT.hasSize,
                                     Literal(data_size, datatype = self.experiment.XSD.int)))
                self.experiment.add((URIRef(transmitted_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                     Literal("Transmitted", datatype = self.experiment.XSD.string)))
                self.experiment.add((URIRef(transmitted_name_uri), self.experiment.DYNAMAT.hasDescription,
                                     Literal("Extracted Transmitted Signal from SG", datatype = self.experiment.XSD.string)))               
                self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                     URIRef(transmitted_name_uri)))
        else: 
            raise ValueError(f"Logic not defined for the amount of {self.transmitted_extracted_signals.shape[1]} Extracted Transmitted Sensor Signals")

        # Add Extracted Time Data
        self.time_sensor_signals_name = self.experiment.get_instances_of_class("dynamat:TimeSensorSignal")[0]        
        time_name_uri = self.time_sensor_signals_name.replace("Sensor", "Extracted") # Extracted Sensor URI
        extracted_signal_class = self.experiment.DYNAMAT.ExtractedSignal
        time_signal_class = self.experiment.DYNAMAT.TimeExtractedSignal   
    
        time_data = np.array(self.extracted_time).astype(np.float32)
        data_size = len(time_data) 
        encoding = "base64Binary"  
    
        if encoding == "base64Binary":
            time_encoded_data = base64.b64encode(time_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
                
        # Add time Extracted Signal
        self.experiment.add((URIRef(time_name_uri), self.experiment.RDF.type, extracted_signal_class))
        self.experiment.add((URIRef(time_name_uri), self.experiment.RDF.type, time_signal_class))
        self.experiment.add((URIRef(time_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.Millisecond))
        self.experiment.add((URIRef(time_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(time_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(time_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(time_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(time_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Time", datatype = self.experiment.XSD.string)))
        self.experiment.add((URIRef(time_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Extracted Time Signal from SG", datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasExtractedSignal,
                                    URIRef(time_name_uri)))
  
        # Add Temperatyre Extracted Signal
        if len(self.experiment.get_instances_of_class("dynamat:TemperatureSensorSignal")) > 0 :
            print("No Temperature Extracted Signal Process Defined.") # Future Update Note!    

                
        ##################################################################################
        #### Step 6: Determine Particle Velocities (Bar interphase velocities) 
        ##################################################################################
        
        self.particle_velocity_1 = self.wave_speed * (self.incident_extracted_signals.iloc[:,0] - self.reflected_extracted_signals.iloc[:,0])       
        print(f"Incident - Specimen Particle Velocity was determined with a max value of {np.min(self.particle_velocity_1):.3f} mm/ms at {self.extracted_time[np.argmin(self.particle_velocity_1)]:.3f} ms")

        self.series_data_class = self.experiment.DYNAMAT.SeriesData
        
        series_name_uri = self.experiment.DYNAMAT["ParticleVelocity_1_Series"]
        series_class_uri = self.experiment.DYNAMAT.ParticleVelocity    
        series_data = np.array(self.particle_velocity_1).astype(np.float32)
        data_size = len(series_data) 
        self.encoding = "base64Binary"  
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.MeterPerSecond))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Front Surface", datatype = self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Incident - Specimen Particle Velocity determined from pulse strains",
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasSeriesData,
                                    URIRef(series_name_uri)))
        self.add_instance_data(self.experiment.DYNAMAT.MeterPerSecond)
        
        self.particle_velocity_2 = self.wave_speed * (self.transmitted_extracted_signals.iloc[:,0]) 
        print(f"Transmitted - Specimen Particle Velocity was determined with a max value of {np.min(self.particle_velocity_2):.3f} mm/ms at {self.extracted_time[np.argmin(self.particle_velocity_2)]:.3f} ms")

        series_name_uri = self.experiment.DYNAMAT["ParticleVelocity_2_Series"]
        series_class_uri = self.experiment.DYNAMAT.ParticleVelocity    
        series_data = np.array(self.particle_velocity_2).astype(np.float32)
        data_size = len(series_data) 
        self.encoding = "base64Binary"  
    
        if self.encoding == "base64Binary":
            series_encoded_data = base64.b64encode(series_data.tobytes()).decode("utf-8")
        else:
            raise ValueError("Unsupported encoding type. Currently only 'base64' is supported.")
            
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, self.series_data_class))
        self.experiment.add((URIRef(series_name_uri), self.experiment.RDF.type, series_class_uri))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasUnits, self.experiment.DYNAMAT.MeterPerSecond))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncodedData,
                                    Literal(series_encoded_data, datatype = self.experiment.XSD.base64Binary)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasEncoding,
                                    Literal(self.encoding, datatype =  self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasSize,
                                    Literal(data_size, datatype = self.experiment.XSD.int)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasLegendName,
                                    Literal("Back Surface", datatype = self.experiment.XSD.string)))
        self.experiment.add((URIRef(series_name_uri), self.experiment.DYNAMAT.hasDescription,
                                    Literal("Transmitted - Specimen Particle Velocity determined from pulse strains",
                                            datatype = self.experiment.XSD.string)))               
        self.experiment.add((URIRef(self.secondary_data_uri), self.experiment.DYNAMAT.hasSeriesData,
                                    URIRef(series_name_uri)))
        self.add_instance_data(self.experiment.DYNAMAT.MeterPerSecond)
        
        print("Saving graph to file...")
        print(f"Graph contains: {self.experiment.len()} triples.")
        with open(self.file_path, "w") as f:
            f.write(self.experiment.serialize("turtle"))

    
    def fetch_gauge_signals(self, gauge_sensor_class):
        """
        Retrieves all instances for a given class as a pandas DataFrame.
        
        Args:
            gauge_sensor_class (str): The class of gauge sensors to fetch signals for.
        
        Returns:
            pd.DataFrame: A DataFrame where each column represents a signal with the column name as the gauge sensor name.
        """
        # Initialize an empty DataFrame to store signals
        signals_df = pd.DataFrame()
    
        # Retrieve all sensor instances of the given class
        sensor_data_instances = self.experiment.get_instances_of_class(gauge_sensor_class)
    
        for sensor_name in sensor_data_instances:
            # Fetch relevant properties for the sensor
            signal_data = self.experiment.get_objects(sensor_name, "dynamat:hasEncodedData")[0]
            signal_encoding = self.experiment.get_objects(sensor_name, "dynamat:hasEncoding")[0]
            signal_size = int(self.experiment.get_objects(sensor_name, "dynamat:hasSize")[0])
            signal_units = self.experiment.get_objects(sensor_name, "dynamat:hasUnits")[0]
            signal_gauge = self.experiment.get_objects(sensor_name, "dynamat:hasStrainGauge")[0]
    
            try:
                if signal_encoding == "base64Binary":
                    # Decode the base64 string into bytes
                    signal_data_decoded = base64.b64decode(signal_data)
                    
                    # Convert the bytes to a NumPy array of float32
                    signal_data_decoded = np.frombuffer(signal_data_decoded, dtype=np.float32) 
                    
                    # Ensure the size matches the expected size
                    if len(signal_data_decoded) != signal_size:
                        raise ValueError(f"Decoded data size ({len(signal_data_decoded)}) does not match expected size ({signal_size}).")
                    
                    if signal_units == "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Volts": 
                        try:
                            gauge_properties = self.fetch_gauge_properties(signal_gauge)
                            gauge_cal_resistance = gauge_properties["SG_CalibrationResistance"]
                            gauge_cal_voltage = gauge_properties["SG_CalibrationVoltage"]
                            gauge_factor = gauge_properties["SG_GaugeFactor"]
                            gauge_resistance = gauge_properties["SG_Resistance"]
                        
                            signal_data_decoded = self.voltage_to_strain(
                                signal_data_decoded, 
                                gauge_resistance, 
                                gauge_factor, 
                                gauge_cal_voltage, 
                                gauge_cal_resistance
                            )
                        except KeyError as e:
                            print(f"Missing key in gauge properties: {e}. Ensure all required keys (SG_CalibrationResistance, SG_CalibrationVoltage, SG_GaugeFactor, SG_Resistance) are present.")
                        except Exception as e:
                            print(f"Error converting voltage signal for {sensor_name}: {e}. Please verify the data and property names.")
                   
                    # Add the signal to the DataFrame with the sensor name as the column header
                    signals_df[sensor_name] = signal_data_decoded
                
            except Exception as e:
                print(f"Error processing {sensor_name}: {e}")
    
        return signals_df  
        
    def fetch_sensor_signals(self, sensor_class):
        """
        Retrieves all instances for a given sensor class as a pandas DataFrame.
        
        Args:
            sensor_class (str): The class of sensors to fetch signals for.
        
        Returns:
            pd.DataFrame: A DataFrame where each column represents a signal with the column name as the sensor name.
        """
        # Initialize an empty DataFrame to store signals
        signals_df = pd.DataFrame()
    
        # Retrieve all sensor instances of the given class
        sensor_data_instances = self.experiment.get_instances_of_class(sensor_class)
    
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
                    
                    # Check for valid units
                    valid_units = {
                        "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Millisecond",
                        "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#DegreesCelsius"
                    }
                    
                    if signal_units not in valid_units:
                        raise ValueError(f"Incorrect unit specified for {sensor_name}: {signal_units}")
                        
                    # Add the signal to the DataFrame with the sensor name as the column header
                    signals_df[sensor_name] = signal_data_decoded
                
            except Exception as e:
                print(f"Error processing {sensor_name}: {e}")
    
        return signals_df

    def fetch_gauge_properties(self, gauge_uri):
        """
        Retrieves values from the gauge instance definition dynamically based on the graph content.
    
        Args:
            gauge_uri (str): The URI of the gauge instance.
    
        Returns:
            dict: A dictionary mapping property names (e.g., "CalibrationVoltage") to their values.
        """
        try:
            # SPARQL query to fetch all strain gauge properties
            query = f"""
            PREFIX : <https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#>
            SELECT ?property ?value WHERE {{
                <{gauge_uri}> :hasStrainGaugeProperty ?property .
                ?property :hasValue ?value .
            }}
            """
            results = self.experiment.query(query)
            
            # Organize properties into a dictionary
            gauge_properties = {}
            for row in results:
                property_uri = str(row.property)
                property_value = float(row.value)  # Assuming numerical values for properties
                # Extract the property name from the URI (e.g., "CalibrationVoltage" from "dynamat:CalibrationVoltage")
                property_name = property_uri.split("#")[-1]
                gauge_properties[property_name] = property_value
    
            return gauge_properties
    
        except Exception as e:
            print(f"Error fetching gauge properties for {gauge_uri}: {e}")
            return {}     

    def voltage_to_strain(self, voltage_array, gauge_res, gauge_factor, cal_voltage, cal_resistance):
        """
        Converts a measured voltage from a strain gauge into strain using the provided parameters.
            
        Parameters:
        ----------
        voltage : float
            The measured voltage from the strain gauge (in volts).
        gauge_res : float
            The resistance of the strain gauge (in ohms).
        gauge_factor : float
            The gauge factor or sensitivity coefficient of the strain gauge (unitless).
        cal_voltage : float
            The calibration voltage applied to the strain gauge circuit (in volts).
        cal_resistance : float
            The resistance of the calibration resistor in the strain gauge circuit (in ohms).
                
        Returns:
        -------
        float
            The calculated strain value (unitless, as strain is dimensionless).
            
        """    
        conversion_factor = gauge_res / (cal_voltage * gauge_factor * (gauge_res + cal_resistance))
        
        strain =  voltage_array * conversion_factor
        return strain         

    def determine_wave_speed(self):
        """
        Logic to fetch or determine wave speed based on the test type case
        """
        self.bars_uri = ["dynamat:IncidentBar", "dynamat:TransmittedBar"]
        if self.test_type == "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SpecimenTest":
            try:
                self.bars_wave_speeds = []
        
                for bar_uri in self.bars_uri:
                    # Fetch the instance URI for the bar
                    bar_instance_uris = self.experiment.get_instances_of_class(bar_uri)
                    if not bar_instance_uris:
                        raise ValueError(f"No instances found for bar class {bar_uri}.")
                    bar_instance_uri = bar_instance_uris[0]  # Assuming there's only one instance per class
        
                    # Fetch properties for the bar
                    bar_properties_uris = self.experiment.get_objects(bar_instance_uri, "dynamat:hasMechanicalProperty")
                    if not bar_properties_uris:
                        raise ValueError(f"No mechanical properties found for bar instance {bar_instance_uri}.")
        
                    # Fetch and process wave speed
                    for prop in bar_properties_uris:
                        if "WaveSpeed" in prop:
                            bar_wave_speed = self.experiment.get_objects(prop, "dynamat:hasValue")
                            if not bar_wave_speed:
                                raise ValueError(f"No value found for WaveSpeed in property {prop}.")
                            self.bars_wave_speeds.append(float(bar_wave_speed[0]))
        
                # Validate wave speed count
                if len(self.bars_wave_speeds) != 2:
                    raise ValueError(f"Bar wave speeds do not match the expected size of 2. Current len: {len(self.bars_wave_speeds)}")
        
                # Calculate the average wave speed
                wave_speed = np.mean(self.bars_wave_speeds)

                # Determine Test Wave Speed
                bars_gauge_distances = self.fetch_bar_gauge_distances()
                specimen_uri = self.experiment.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_properties_uris = self.experiment.get_objects(specimen_uri, "dynamat:hasDimension")
                for prop in specimen_properties_uris:
                    if "OriginalLength" in prop:
                        specimen_length = float(self.experiment.get_objects(prop, "dynamat:hasValue")[0])
                        pulse_speed = self.calculate_wave_speed(
                            self.time_sensor_signals.iloc[:, 0],
                            self.incident_sensor_signals.iloc[:, 0],
                            bars_gauge_distances[0],
                            self.transmitted_sensor_signals.iloc[:, 0],
                            bars_gauge_distances[1],
                            specimen_length)
       
                
                print(f'Bar Wave Speed: {wave_speed:.3e} m/s')
                print(f'Specimen Length: {specimen_length:.3e} mm')
                print(f'Test Wave Speed: {pulse_speed:.3e} m/s')
                return wave_speed, pulse_speed
                
            except ValueError as e:
                print(f"ValueError: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")        
                
        elif self.test_type == "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#PulseTest":

            try:
                bars_gauge_distances = self.fetch_bar_gauge_distances()
                    # Calculate wave speed
                wave_speed = self.calculate_wave_speed(
                    self.time_sensor_signals.iloc[:, 0],
                    self.incident_sensor_signals.iloc[:, 0],
                    bars_gauge_distances[0],
                    self.transmitted_sensor_signals.iloc[:, 0],
                    bars_gauge_distances[1],
                    0
                    )
                pulse_speed = wave_speed
                print(f'Bar Wave Speed: {wave_speed:.3e} mm/ms')
                print(f'No Specimen, therefore the Test Wave Speed is the same') 
                print(f'Test Wave Speed: {pulse_speed:.3e} mm/ms') 
    
                self.save_wave_speed(wave_speed)
                return wave_speed, pulse_speed
                
            except ValueError as e:
                print(f"ValueError encountered: {e}")
            except KeyError as e:
                print(f"KeyError encountered: {e}")
            except IndexError as e:
                print(f"IndexError encountered: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        else: 
            print("Wave Speed not calculated, check logic")

    def fetch_bar_gauge_distances(self):
        try:
            bars_gauge_dist = []
            
            for bar_uri in self.bars_uri:                
                # Fetch the instance URI for the bar
                bar_instance_uri = self.experiment.get_instances_of_class(bar_uri)
                if not bar_instance_uri:
                    raise ValueError(f"No instances found for bar class {bar_uri}.")
                bar_instance_uri = bar_instance_uri[0]  # Assuming there's only one instance per class
            
                # Fetch dimensions for the bar
                bar_sg_uris = self.experiment.get_objects(bar_instance_uri, "dynamat:hasStrainGauge")
                if not bar_sg_uris:
                    raise ValueError(f"No dimensions found for bar instance {bar_instance_uri}.")
                    
                sg_dimensions_uris = self.experiment.get_objects(bar_sg_uris[0], "dynamat:hasDimension")
                if not sg_dimensions_uris:
                    raise ValueError(f"No dimensions found for bar instance {bar_sg_uris}.")
            
                for dimension in sg_dimensions_uris:
                    if "Distance" in dimension:
                        # Fetch and convert the value
                        sg_gauge_distance = self.experiment.get_objects(dimension, "dynamat:hasValue")
                        if not sg_gauge_distance:
                            raise ValueError(f"No value found for dimension {dimension}.")
                        sg_gauge_distance = float(sg_gauge_distance[0])
                        bars_gauge_dist.append(sg_gauge_distance)
            
            # Check if the number of gauge distances is correct
            if len(bars_gauge_dist) != 2:
                raise ValueError(f"Bar gauge distances do not match the expected size of 2. Current len: {len(bars_gauge_dist)}")
            print(f"Strain Gauge Distances for Incident and Transmitted Bar : {bars_gauge_dist} mm")
            return bars_gauge_dist

        except ValueError as e:
            print(f"ValueError encountered: {e}")
        except KeyError as e:
            print(f"KeyError encountered: {e}")
        except IndexError as e:
            print(f"IndexError encountered: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
    
    def calculate_wave_speed(self, time, incident_pulse, incident_gauge_dist, transmitted_pulse,
                             transmitted_gauge_dist, specimen):
        """
        Calculates the wave speed in a system based on time, pulse signals, and distances.
        
        Parameters:
        -----------
        time : array-like
            The time data corresponding to the pulses. 
        incident_pulse : array-like
            Signal data from the incident gauge.
        incident_gauge_dist : float
            Distance between the incident gauge and the sample.
        transmitted_pulse : array-like
            signal data from the transmitted gauge.
        transmitted_gauge_dist : float
            Distance between the transmitted gauge and the sample.
        
        Returns:
        --------
        wave_speed : float
            The calculated wave speed in the system based on the time difference between the 90% points of 
            the incident and transmitted pulses and the total travel distance.    
        """
        max_value_incident = np.min(incident_pulse)
        max_index_incident = np.argmin(incident_pulse) 
        
        max_value_transmitted = np.min(transmitted_pulse)
        max_index_transmitted = np.argmin(transmitted_pulse)  
        
        # Find the 90% of the max value
            
        ninety_percent_value_incident = 0.9 * max_value_incident
        ninety_percent_value_transmitted = 0.9 * max_value_transmitted
        
        # Find the time where the signal first crosses 10%
        ninety_percent_index_incident = np.where(incident_pulse <= ninety_percent_value_incident)[0][0]        
        ninety_percent_index_transmitted = np.where(transmitted_pulse <= ninety_percent_value_transmitted)[0][0]

        delta_t = time[ninety_percent_index_transmitted] - time[ninety_percent_index_incident]
        distance_x = incident_gauge_dist + specimen + transmitted_gauge_dist 
        
        wave_speed = distance_x / delta_t    
            
        return wave_speed    
   
    def determine_pulse_duration(self, striker_length, wave_speed_striker):
        """
        Calculates the loading duration for a stress wave.
    
        Parameters:
            striker_length (float): The length of the bar (milimeters).
            wave_speed_striker (float): The speed of the stress wave (milimiters per milisecond).
    
        Returns:
            float: The loading duration (T) in seconds.
        """
        T = (2*striker_length) / wave_speed_striker 
        print(f'Loading Duration: {T:.2e} miliseconds')
        
        return T
    
    def determine_incident_stress_pulse(self, density_b, C_b, V_st):
        """
        Calculates the amplitude of the incident stress pulse.
    
        Parameters:
            density_b (float): The density of the bar (kg/mm^3).
            C_b (float): The speed of the stress wave in the bar (m/s).
            V_st (float): The particle velocity of the stress wave (m/s) (striker velocity).
    
        Returns:
            float: The amplitude of the incident stress pulse (GPa).
        """
        sigma_I = 1/2 * density_b * C_b * V_st 
        print(f'Amplitude Incident Stress Pulse: {sigma_I:.4e} GPa')
        
        return sigma_I
    
    def determine_incident_strain_pulse(self, C_b, V_st):
        """
        Calculates the amplitude of the incident strain pulse.
    
        Parameters:
            C_b (float): The speed of the stress wave in the bar (m/s).
            V_st (float): The particle velocity of the stress wave (m/s).
    
        Returns:
            float: The amplitude of the incident strain pulse (m/m).
        """
        epsilon_I = 1/2 * (V_st / C_b)
        print(f'Amplitude Incident Strain Pulse: {epsilon_I:.2e} mm/mm')
        return epsilon_I
        

    def voltage_to_strain(self, voltage_array, gauge_res, gauge_factor, cal_voltage, cal_resistance):
        """
        Converts a measured voltage from a strain gauge into strain using the provided parameters.
        
        Parameters:
        ----------
        voltage_array : np.array(float32)
            The measured voltage from the strain gauge (in volts).
        gauge_res : float
            The resistance of the strain gauge (in ohms).
        gauge_factor : float
            The gauge factor or sensitivity coefficient of the strain gauge (unitless).
        cal_voltage : float
            The calibration voltage applied to the strain gauge circuit (in volts).
        cal_resistance : float
            The resistance of the calibration resistor in the strain gauge circuit (in ohms).
            
        Returns:
        -------
        np,array(float32)
            The calculated strain value (unitless, as strain is dimensionless).

        """    
        
        conversion_factor = gauge_res / (cal_voltage * gauge_factor * (gauge_res + cal_resistance))
    
        strain =   voltage_array * conversion_factor
        return strain


    def extract_pulse_data(self, strain_signal, pulse_points, interpolation = 1, min_search = False, cutoff = 1e-5, offset = 0):
        """
        Extracts a segment of the strain signal corresponding to a pulse and applies optional interpolation and offset.
    
        This function analyzes the strain signal to extract the part of the signal where the pulse occurs.
        The signal is searched for the point where it crosses 70% and 20% of its maximum or minimum value,
        depending on whether `min_search` is True or False. 
        
        It then extracts a specified number of points 
        (`pulse_points`) starting from a zero-crossing or near-zero point in the signal.
        
        Optional interpolation can be applied to the extracted signal.
    
        Parameters:
            strain_signal (np.array): The input strain signal array.
            pulse_points (int): The number of data points to extract from the signal starting from the zero-crossing.
            interpolation (int, optional): The factor by which to interpolate the extracted signal. Defaults to 1 (no interpolation).
            min_search (bool, optional): If True, the function searches for the minimum value in the signal. 
                                         If False, it searches for the maximum value. Defaults to False.
            cutoff (float, optional): The cutoff value for detecting near-zero points in the signal. Defaults to 1e-5.
    
        Returns:
            np.array: The extracted segment of the strain signal, interpolated if `interpolation` > 1.
        
        Raises:
            IndexError: If the extraction points are out of bounds for the input signal.
        """
        
        if min_search:
            max_value = np.min(strain_signal)
            max_index = np.argmin(strain_signal)        
        else: 
            max_value = np.max(strain_signal)
            max_index = np.argmax(strain_signal) 
        
        # Find the 10% and 90% of the max value
        ten_percent_value = 0.1 * max_value
        ninety_percent_value = 0.9 * max_value
    
        # Find the time where the signal first crosses 10%
        if min_search:
            ninety_percent_index = np.where(strain_signal <= ninety_percent_value)[0][0]
            ten_percent_index = np.where(strain_signal >= ten_percent_value)[0]
            zero_index = np.where(strain_signal >= (-1 * cutoff))[0]
            
            ten_percent_index = ten_percent_index[ten_percent_index <= ninety_percent_index][-1] 
            zero_index = zero_index[zero_index <= ten_percent_index][-1]
            
        else:
            ninety_percent_index = np.where(strain_signal >= ninety_percent_value)[0][0]
            ten_percent_index = np.where(strain_signal <= ten_percent_value)[0]
            zero_index = np.where(strain_signal <= cutoff)[0]
            
            ten_percent_index = ten_percent_index[ten_percent_index <= ninety_percent_index][-1] 
            zero_index = zero_index[zero_index <= ten_percent_index][-1]
        
        extracted_signal = strain_signal[(zero_index-offset) : (zero_index - offset) + pulse_points]
        
        # Apply interpolation based on the interpolation variable
        if interpolation >= 1:
            x = np.arange(len(extracted_signal))
            x_interp = np.linspace(0, len(extracted_signal) - 1, len(extracted_signal) * interpolation)
            
            # Perform interpolation using np.interp for linear interpolation
            interpolated_signal = np.interp(x_interp, x, extracted_signal)
            
            return interpolated_signal
        
        else:
            return extracted_signal

    def save_wave_speed(self, wave_speed):
        """ 
        Save determined wave speed as the bar's wave speed properties
        """
        bars_uris = self.bars_uri
        bars_uris.append("dynamat:StrikerBar") # Add data to striker bar too, but does not edit global list definition
        for bar_uri in bars_uris:
        # Fetch the instance URI for the bar
            bar_instance_uri = self.experiment.get_instances_of_class(bar_uri)
            bar_instance_uri = str(bar_instance_uri[0]).split('#')[-1]  # Assuming there's only one instance per class
            bar_instance_wave_speed_uri = self.experiment.DYNAMAT[f"{bar_instance_uri}_WaveSpeed"] 
            
            self.experiment.set((URIRef(bar_instance_wave_speed_uri), self.experiment.DYNAMAT.hasValue,
                                 Literal(wave_speed, datatype = self.experiment.XSD.float)))
            print(f"Setting new value for {bar_instance_wave_speed_uri} with new value of : {wave_speed} m/s")


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