from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from rdflib import Graph, Namespace, URIRef, Literal
from scripts.rdf_wrapper import RDFWrapper
from scripts.unit_converter import SIConverter
from scripts.SHPB_SignalExtract import SignalExtractor
from scripts.SHPB_SeriesData import SeriesData
import pandas as pd
import numpy as np

class SecondaryDataWidget(QWidget):
    def __init__(self, ontology_path, experiment_temp_file_path):
        super().__init__()
        
        self.file_path = experiment_temp_file_path
        self.ontology_path = ontology_path

        # Main layout for the tab
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Example UI components for secondary data analysis
        self.label = QLabel("Secondary Data Analysis")
        self.layout.addWidget(self.label)

        self.analyze_button = QPushButton("Perform Analysis")
        self.analyze_button.clicked.connect(self.perform_analysis)
        self.layout.addWidget(self.analyze_button)

    def perform_analysis(self):
        """
        Example method to perform analysis on the secondary data.
        """
        print(f"Performing analysis using temp file: {self.file_path}")        
        self.primary_data = RDFWrapper(self.file_path)

        # Convert units
        SIConverter(self.ontology_path, self.file_path)

        # Extract Signals 
        SignalExtractor(self.ontology_path, "data/data_out_converter.ttl")

        self.test_type = self.primary_data.get_instances_of_class("dynamat:TestType")[0]
        if URIRef(self.test_type) == self.primary_data.DYNAMAT.SpecimenTest:
            print("Determining series data for specimen test experiment...")
            SeriesData(self.ontology_path, "data/data_out_converter_002.ttl")

        

        



