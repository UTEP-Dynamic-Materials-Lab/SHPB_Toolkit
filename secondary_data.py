from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from rdflib import Graph, Namespace, URIRef, Literal
from scripts.rdf_wrapper import RDFWrapper
from scripts.unit_converter import SIConverter
from scripts.SHPB_SignalExtract import SignalExtractor
from scripts.SHPB_SeriesData import SeriesData
from scripts.validator import ValidateData
import pandas as pd
import numpy as np
import os

class SecondaryDataWidget(QWidget):
    def __init__(self, ontology_path, experiment_temp_file_path):
        super().__init__()
        
        self.file_path = experiment_temp_file_path
        self.ontology_path = ontology_path

        # Main layout for the tab
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.analyze_button = QPushButton("Perform Analysis")
        self.analyze_button.clicked.connect(self.perform_analysis)
        self.layout.addWidget(self.analyze_button)

    def perform_analysis(self):
        """
        Example method to perform analysis on the secondary data.
        """
        print(f"Performing analysis using temp file: {self.file_path}")        
        self.primary_data = RDFWrapper(self.file_path)

        self.metadata = self.primary_data.get_instances_of_class("dynamat:Metadata")[0]
        self.test_name = self.primary_data.get_objects(self.metadata, "dynamat:hasTestName")[0]
        self.testing_conditions = self.primary_data.get_instances_of_class("dynamat:TestingConditions")[0]
        self.test_mode = self.primary_data.get_objects(self.testing_conditions, "dynamat:hasTestMode")[0]
        self.test_type = self.primary_data.get_objects(self.testing_conditions, "dynamat:hasTestType")[0]
        self.test_temperature = self.primary_data.get_objects(self.testing_conditions, "dynamat:hasTestTemperature")[0]

        #########################################
        ### Metadata Unit Conversion
        #########################################  
        try:
            print(f"Starting Unit conversion for {self.test_name}")
            SIConverter(self.ontology_path, self.file_path)
            print(f"Finished Unit conversion for {self.test_name}")
        except Exception as e:
            print(f"Error in unit conversion: {e}")
        
        # Add Validator Shapes
        validator = ValidateData(self.file_path)
        shapes_folder = os.path.join(os.getcwd(), "ontology", "shapes")
        self.validation_state = False # start with negative validation state.
        
        #########################################
        ### Metadata Validation
        #########################################    
        try:
            validation_results = validator.validate_with_shacl(os.path.join(shapes_folder, "metadata_shape.ttl"))
            if validation_results["conforms"] == True:
                print("Metadata Validation Conforms:", validation_results["conforms"])
                self.validation_state = True
    
            else:
                self.validation_state = False
                print("Metadata Validation failed.")
                print(validation_results["report_text"]) 
                report_path = os.path.join(os.getcwd(), "ontology", "reports", "metadata_validation_report.ttl")
                validation_results["report_graph"].serialize(destination=report_path, format="turtle")
                print(f"Validation report saved to {report_path}")
                print(f"See ontology/reports/metadata_validation_report.ttl for more information")      
        
        except Exception as e:
            print(f"Error Validating Metadata: {e}")
            self.validation_state = False

        #########################################
        ### Test Type Validation PULSE/SPECIMEN
        #########################################    
        try:
            if URIRef(self.test_type) == self.primary_data.DYNAMAT.SpecimenTest:
                print(f"Starting Specimen Test validation for {self.test_name}")
                validation_results = validator.validate_with_shacl(os.path.join(shapes_folder, "specimen_test_shape.ttl"))
            elif URIRef(self.test_type) == self.primary_data.DYNAMAT.PulseTest:
                print(f"Starting Pulse Test validation for {self.test_name}")
                validation_results = validator.validate_with_shacl(os.path.join(shapes_folder, "pulse_test_shape.ttl"))
            else: 
                print(f"Test Type is not in accordance with available SHACL Shapes")
                
            if validation_results["conforms"] == True:
                print("Test Type Validation Conforms:", validation_results["conforms"])
                self.validation_state = True
    
            else:
                self.validation_state = False
                print("Test Type Validation failed.")
                print(validation_results["report_text"]) 
                report_path = os.path.join(os.getcwd(), "ontology", "reports", "test_type_validation_report.ttl")
                validation_results["report_graph"].serialize(destination=report_path, format="turtle")
                print(f"Validation report saved to {report_path}")
                print(f"See ontology/reports/test_type_validation_report.ttl for more information")      
        
        except Exception as e:
            print(f"Error Validating Test Type: {e}")
            self.validation_state = False

        #########################################
        ### Test Mode Validation LAB/FEA
        #########################################    
        try:
            if URIRef(self.test_mode) == self.primary_data.DYNAMAT.LABMode:
                print(f"Starting LAB Mode validation for {self.test_name}")
                validation_results = validator.validate_with_shacl(os.path.join(shapes_folder, "lab_test_shape.ttl"))
            elif URIRef(self.test_mode) == self.primary_data.DYNAMAT.FEAMode:
                print(f"Starting FEA Mode validation for {self.test_name}")
                validation_results = validator.validate_with_shacl(os.path.join(shapes_folder, "fea_test_shape.ttl"))
            else: 
                print(f"Test Mode is not in accordance with available SHACL Shapes")
                
            if validation_results["conforms"] == True:
                print("Test Mode Validation Conforms:", validation_results["conforms"])   
                self.validation_state = True
    
            else:
                self.validation_state = False
                print("Test Mode Validation failed.")
                print(validation_results["report_text"]) 
                report_path = os.path.join(os.getcwd(), "ontology", "reports", "test_mode_validation_report.ttl")
                validation_results["report_graph"].serialize(destination=report_path, format="turtle")
                print(f"Validation report saved to {report_path}")
                print(f"See ontology/reports/test_mode_validation_report.ttl for more information")      
        
        except Exception as e:
            print(f"Error Validating Test Mode: {e}")
            self.validation_state = False

        #########################################
        ### Test Temperature Validation
        #########################################    
        try:
            if URIRef(self.test_temperature) == self.primary_data.DYNAMAT.RoomTemperature:
                print(f"Starting Room Temperature validation for {self.test_name}")
                validation_results = validator.validate_with_shacl(os.path.join(shapes_folder, "primary_data_RT_shape.ttl"))
            elif URIRef(self.test_temperature) == self.primary_data.DYNAMAT.HighTemperature:
                print(f"Starting High Temperature validation for {self.test_name}")
                validation_results = validator.validate_with_shacl(os.path.join(shapes_folder, "primary_data_HT_shape.ttl"))
            else: 
                print(f"Test Temperature is not in accordance with available SHACL Shapes")
                
            if validation_results["conforms"] == True:
                print("Test Temperature Validation Conforms:", validation_results["conforms"])   
    
            else:
                print("Test Temperature Validation failed.")
                print(validation_results["report_text"]) 
                report_path = os.path.join(os.getcwd(), "ontology", "reports", "test_temp_validation_report.ttl")
                validation_results["report_graph"].serialize(destination=report_path, format="turtle")
                print(f"Validation report saved to {report_path}")
                print(f"See ontology/reports/test_temp_validation_report.ttl for more information")      
        
        except Exception as e:
            print(f"Error Validating Test Mode: {e}")
                
        ##############################################
        ### Secondary Data 
        ###############################################
        print(f"Starting Secondary Data Analysis for {self.test_name}")
        #SignalExtractor(self.ontology_path, self.file_path)
        
        if URIRef(self.test_type) == self.primary_data.DYNAMAT.SpecimenTest:
            print("Determining series data for specimen test experiment...")
            #SeriesData(self.ontology_path, self.file_path)

        ##############################################
        ### Add data to database
        ###############################################

        if self.validation_state == True:

            self.graph = Graph()
            self.graph.parse(self.file_path, format="turtle")   
            # Bind namespaces for easier readability
            self.graph.bind("dynamat",  self.primary_data.DYNAMAT)
            self.graph.bind("owl",  self.primary_data.OWL)
            self.graph.bind("rdf",  self.primary_data.RDF)
            self.graph.bind("xml",  self.primary_data.XML)
            self.graph.bind("xsd",  self.primary_data.XSD)
            self.graph.bind("rdfs",  self.primary_data.RDFS)
            
            print("Adding new file to database...")
            print(f"Graph contains: {len(self.graph)} triples.")
            result_file_path = os.path.join("data", f"{self.test_name}.ttl")
            with open(result_file_path, "w") as f:
                f.write(self.graph.serialize(format="turtle"))
    
            #Add Data to widget:
            self.label = QLabel(f"Secondary Data Analysis for {self.test_name}")
            self.layout.addWidget(self.label)        
            self.label = QLabel(f"Test Mode : {self.test_mode.split('#')[-1]}")
            self.layout.addWidget(self.label)
            self.label = QLabel(f"Test Type : {self.test_type.split('#')[-1]}")
            self.layout.addWidget(self.label)
            self.label = QLabel(f"Test Temperature : {self.test_temperature.split('#')[-1]}")
            self.layout.addWidget(self.label)
    
            """
    	    try:
    	    	self.result_file = RDFWrapper(result_file_path)
                data_properties = ["SHPBSpecimen", "SensorSignal", "ExtractedSignal", "SeriesData" ]
                for prop in data_properties:
                    prop_instances = self.result_file.get_instances_of_class(f"dynamat:{prop}")
                    prop_len = len(prop_instances)
                    self.label = QLabel(f"Test contains {prop_len} {prop}")
                    self.layout.addWidget(self.label)
                     
                    self.label = QLabel(f"Test contains 0 {prop}")
                    self.layout.addWidget(self.label)
        
                pulse_properties = ["PulseLength", "PulseSpeed", "PulseStrainAmplitude", "PulseStressAmplitude" ] 
                for properties in pulse_properties:    
                
                    prop_instances = self.result_file.get_instances_of_class(f"dynamat:{properties}")[0]
                    prop_units = self.result_file.get_objects(prop_instances, "dynamat:hasUnits")[0]
                    prop_units = self.result_file.get_objects( prop_units, "dynamat:hasAbbreviation")[0]                    
                    prop_value = float(self.result_file.get_objects(prop_instances, "dynamat:hasValue")[0])
                           
                    self.label = QLabel(f"Test {prop_instances.split('#')[-1]} has value of {prop_value:.4f} {prop_units}")
                    self.layout.addWidget(self.label)
    
             except:
                self.label = QLabel(f"Test {properties} has not correct calculated values")
                self.layout.addWidget(self.label)
            """

        else:
            print(f"{self.test_name} not added because it does not passed all validation stages")
            print(f"See log info and refer to documentation")
            self.label = QLabel(f"{self.test_name} failed validation, and was not added to the database")
            self.layout.addWidget(self.label) 
             

        

