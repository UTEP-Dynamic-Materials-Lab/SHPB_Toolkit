from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QSpinBox, QPushButton, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtCore import pyqtSignal
from rdflib import Graph, Namespace, URIRef
from GUI.components.common_widgets import MaterialSelector, ClassInstanceSelection, SetDefaults

class TestDescriptionWidget(QWidget):
    current_test_mode = pyqtSignal(str) # Propagates the FEA/LAB Mode signals to other tabs
    current_test_type = pyqtSignal(str) # Propagates the Specimen/Pulse Signals to other tabs 
    current_specimen_material = pyqtSignal(str)
    current_test_name = pyqtSignal(str)
       
    def __init__(self, ontology_path, test_config, experiment_temp_file):
        super().__init__()
        self.setWindowTitle("Test Description")
        self.setGeometry(100, 100, 600, 450)

        self.test_config = test_config        
        self.experiment = experiment_temp_file

        self.ontology = Graph()
        self.ontology_path = ontology_path
        self.ontology.parse(self.ontology_path, format="turtle")
        self.namespace = Namespace("https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#")

        # Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_ui()
        
        self.layout.addStretch()
        self.update_test_name()
    #################################################
    ## WIDGETS INITIALIZATION
    #################################################

    def init_ui(self):
        """Initialize UI components."""      
        
        # Test Name Display
        test_name_label = QLabel("Generated Test Name:")
        self.test_name_display = QLineEdit()
        self.test_name_display.setReadOnly(True)
        self.layout.addWidget(test_name_label)
        self.layout.addWidget(self.test_name_display)

        # Add User Selector
        user_label = QLabel("User:")
        self.layout.addWidget(user_label)
        self.user_selector = ClassInstanceSelection(self.ontology_path, self.experiment.DYNAMAT.User)
        SetDefaults(self.ontology_path, self.test_config.test_user, self.user_selector)
        self.user_selector.currentIndexChanged.connect(self.update_test_name)
        self.user_selector.currentIndexChanged.connect(self.update_user)
        self.layout.addWidget(self.user_selector)

        # Add Date Input
        date_label = QLabel("Test Date:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())  # Set to current date by default
        self.date_input.dateChanged.connect(self.update_test_name) 
        self.layout.addWidget(date_label)
        self.layout.addWidget(self.date_input)
        
        # Add Test Type Selector
        test_type_label = QLabel("Test Type:")
        self.layout.addWidget(test_type_label)
        self.test_type_selector = ClassInstanceSelection(self.ontology_path, self.experiment.DYNAMAT.TestType)
        SetDefaults(self.ontology_path, self.test_config.test_type, self.test_type_selector)
        self.test_type_selector.currentIndexChanged.connect(self.update_test_name)
        self.test_type_selector.currentIndexChanged.connect(self.update_test_type)        
        self.layout.addWidget(self.test_type_selector)

        # Add Material Selector
        material_label = QLabel("Specimen Material:")
        self.layout.addWidget(material_label)
        self.material_selector = MaterialSelector(self.ontology_path, self.experiment.DYNAMAT.Material)
        SetDefaults(self.ontology_path, self.test_config.specimen_material, self.material_selector)
        self.material_selector.currentIndexChanged.connect(self.update_test_name)
        self.material_selector.currentIndexChanged.connect(self.update_material) 
        self.layout.addWidget(self.material_selector)
        
        # Add Test Mode Selector
        test_mode_label = QLabel("Test Mode:")
        self.layout.addWidget(test_mode_label)
        self.test_mode_selector = ClassInstanceSelection(self.ontology_path, self.experiment.DYNAMAT.TestMode)
        SetDefaults(self.ontology_path, self.test_config.test_mode, self.test_mode_selector)
        self.test_mode_selector.currentIndexChanged.connect(self.update_test_name)
        self.test_mode_selector.currentIndexChanged.connect(self.update_test_mode)
        self.layout.addWidget(self.test_mode_selector)

        # Add Environment Selector
        temp_mode_label = QLabel("Temperature Mode:")
        self.layout.addWidget(temp_mode_label)
        self.temp_mode_selector = ClassInstanceSelection(self.ontology_path, self.experiment.DYNAMAT.TestTemperature)
        SetDefaults(self.ontology_path, self.test_config.temp_mode, self.temp_mode_selector)
        self.temp_mode_selector.currentIndexChanged.connect(self.update_test_name)
        self.temp_mode_selector.currentIndexChanged.connect(self.update_temp_mode)        
        self.layout.addWidget(self.temp_mode_selector)

        # Experiment ID
        exp_id_label = QLabel("Experiment ID:")
        self.exp_id_spinbox = QSpinBox()
        self.exp_id_spinbox.setRange(1, 999)
        self.exp_id_spinbox.setValue(1)
        self.exp_id_spinbox.valueChanged.connect(self.update_test_name)
        self.layout.addWidget(exp_id_label)
        self.layout.addWidget(self.exp_id_spinbox)

        # Confirm/Edit Button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.toggle_confirm_edit)
        self.layout.addWidget(self.confirm_button)          

    #################################################
    ## DATA CAPTURE AND RDF GENERATION
    #################################################

    def toggle_confirm_edit(self):
        """Toggle between Confirm and Edit modes."""
        editable = self.confirm_button.text() == "Edit"
        self.user_selector.setEnabled(editable)
        self.date_input.setEnabled(editable)
        self.material_selector.setEnabled(editable)
        self.test_type_selector.setEnabled(editable)
        self.test_mode_selector.setEnabled(editable)
        self.temp_mode_selector.setEnabled(editable)
        self.exp_id_spinbox.setEnabled(editable)

        self.confirm_button.setText("Confirm" if editable else "Edit")

        # Add data to temp file
        if not editable:
            self.experiment.initialize_temp()
            experiment_name_uri = self.experiment.DYNAMAT[str(self.test_name_display.text())]
            metadata_uri = self.experiment.DYNAMAT["Experiment_Metadata"]
            primary_data_uri = self.experiment.DYNAMAT["Experiment_Primary_Data"]
            secondary_data_uri = self.experiment.DYNAMAT["Experiment_Secondary_Data"]
            specimen_uri = self.experiment.DYNAMAT["Test_Specimen"]
            testing_conditions_uri = self.experiment.DYNAMAT["Testing_Conditions"]
            
            # Set Display Name as SHPB Test
            self.experiment.set_triple(str(experiment_name_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.SHPBExperiment))
            self.experiment.add_instance_data(self.experiment.DYNAMAT.SHPBExperiment)

            # Set Metdata, Primary and Secondary Data Objects 
            self.experiment.set_triple(str(metadata_uri), str(self.experiment.RDF.type),
                                       str(self.experiment.DYNAMAT.Metadata))
            self.experiment.set_triple(str(primary_data_uri), str(self.experiment.RDF.type),
                                       str(self.experiment.DYNAMAT.PrimaryData))
            self.experiment.set_triple(str(secondary_data_uri), str(self.experiment.RDF.type), 
                                       str(self.experiment.DYNAMAT.SecondaryData))

            # Assign Metdata, Primary and Secondary Data Objects to SHPB Experiment Instance
            self.experiment.set_triple(str(experiment_name_uri), str(self.experiment.DYNAMAT.hasMetadata),
                                       str(metadata_uri))
            self.experiment.set_triple(str(experiment_name_uri), str(self.experiment.DYNAMAT.hasPrimaryData),
                                       str(primary_data_uri))
            self.experiment.set_triple(str(experiment_name_uri), str(self.experiment.DYNAMAT.hasSecondaryData),
                                       str(secondary_data_uri))
            
            # Set TestName, TestDate and User from selections
            self.experiment.set_triple(str(metadata_uri), str(self.experiment.DYNAMAT.hasTestName),
                                       self.test_name_display.text(), obj_type="string")
            self.experiment.set_triple(str(metadata_uri), str(self.experiment.DYNAMAT.hasTestDate),
                                       self.date_input.date().toString("yyyy-MM-dd"), obj_type="date")
            
            user_uri, user_abbreviation = self.user_selector.currentData()
            self.experiment.set_triple(str(metadata_uri), str(self.experiment.DYNAMAT.hasUser), user_uri)
            self.experiment.add_instance_data(user_uri)
            self.experiment.add_triple(str(user_uri), str(self.experiment.RDF.type), self.experiment.DYNAMAT.User)

            # Set TestType, TestMode and TestTemperature from selections
            test_type_uri, test_type_abbreviation = self.test_type_selector.currentData()
            self.experiment.set_triple(str(testing_conditions_uri), str(self.experiment.RDF.type),
                                       str(self.experiment.DYNAMAT.TestingConditions))            
            self.experiment.set_triple(str(metadata_uri), str(self.experiment.DYNAMAT.hasTestingConditions),
                                       testing_conditions_uri)
            self.experiment.set_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasTestType),
                                       test_type_uri)
            self.experiment.add_instance_data(test_type_uri)
            self.experiment.add_triple(str(test_type_uri), str(self.experiment.RDF.type),
                                       self.experiment.DYNAMAT.TestType)


            test_mode_uri, test_mode_abbreviation = self.test_mode_selector.currentData()
            self.experiment.set_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasTestMode),
                                       test_mode_uri)
            self.experiment.add_instance_data(test_mode_uri)
            self.experiment.add_triple(str(test_mode_uri), str(self.experiment.RDF.type),
                                       self.experiment.DYNAMAT.TestMode)


            temp_mode_uri, temp_mode_abbreviation = self.temp_mode_selector.currentData()
            self.experiment.set_triple(str(testing_conditions_uri), str(self.experiment.DYNAMAT.hasTestTemperature),
                                       temp_mode_uri)
            self.experiment.add_instance_data(temp_mode_uri)
            self.experiment.add_triple(str(temp_mode_uri), str(self.experiment.RDF.type),
                                       self.experiment.DYNAMAT.TestTemperature)

            # Set Specimen instance and Material when Specimen mode selected            
            if test_type_abbreviation == "Specimen":                
                material_uri, material_abbreviation = self.material_selector.currentData()
                self.experiment.set_triple(str(specimen_uri), str(self.experiment.RDF.type),
                                           self.experiment.DYNAMAT.SHPBSpecimen) 
                self.experiment.add_triple(str(specimen_uri), str(self.experiment.RDF.type),
                                           self.experiment.DYNAMAT.Specimen) 
                self.experiment.set_triple(str(metadata_uri), str(self.experiment.DYNAMAT.hasSpecimen),
                                           specimen_uri)
                self.experiment.set_triple(str(specimen_uri), str(self.experiment.DYNAMAT.hasMaterial),
                                           material_uri)                
                self.experiment.add_instance_data(material_uri)
                self.experiment.add_triple(str(material_uri), str(self.experiment.RDF.type),
                                           self.experiment.DYNAMAT.Material)
            else: 
                print("No Specimen Class added to file, because PULSE Test Type Selected")
                try: 
                    self.experiment.remove_triple(str(metadata_uri), str(self.experiment.DYNAMAT.hasSpecimen), specimen_uri)
                    self.experiment.remove_triple(str(specimen_uri), str(self.experiment.DYNAMAT.hasMaterial), material_uri)
                    self.experiment.remove_triple(str(material_uri), str(self.experiment.RDF.type), self.experiment.DYNAMAT.Material)
                except: 
                    None
            self.experiment.save()       

    #################################################
    ## TEST NAME GENERATION FIELD
    #################################################
    
    def update_test_name(self):
        """Update the test name dynamically."""
        user_uri, user_abbreviation = self.user_selector.currentData()
        date = self.date_input.date().toString("yyyyMMdd")        
        test_type_uri, _ = self.test_type_selector.currentData()
        test_mode_uri, _ = self.test_mode_selector.currentData() 
        temp_mode_uri, _ = self.temp_mode_selector.currentData()
        test_type_uri = URIRef(test_type_uri) if isinstance(test_type_uri, str) else test_type_uri
        test_mode_uri = URIRef(test_mode_uri) if isinstance(test_mode_uri, str) else test_mode_uri
        temp_mode_uri= URIRef(temp_mode_uri) if isinstance(temp_mode_uri, str) else temp_mode_uri

        try:
            if isinstance(test_type_uri, URIRef) and test_type_uri == self.experiment.DYNAMAT.SpecimenTest:
                material_uri, material_abbreviation = self.material_selector.currentData()
            else:
                material_abbreviation = "PULSE" 
                
            if isinstance(test_mode_uri, URIRef) and test_mode_uri == self.experiment.DYNAMAT.LABMode:
                lab_fea = "LAB"
            else: lab_fea = "FEA"
                
            if isinstance(temp_mode_uri, URIRef) and temp_mode_uri == self.experiment.DYNAMAT.RoomTemperature:
                ht_rt = "RT"
            else: ht_rt = "HT"        
            experiment_id = f"{self.exp_id_spinbox.value():03}"
        
            if user_abbreviation and material_abbreviation:
                test_name = f"{user_abbreviation}_{date}_{material_abbreviation}_{lab_fea}_{ht_rt}_{experiment_id}"
                self.test_name_display.setText(test_name)
                self.update_global_name(test_name)

        except: self.test_name_display.setText("Incomplete Input: Please fill all fields")
    
    def update_global_name(self, test_name):
        """Update the global test name for later triplet assignment."""
        self.test_config.test_name = test_name
        self.current_test_name.emit(test_name)
         
    #################################################
    ## MATERIAL SELECTION FIELD
    #################################################
    def update_material(self):
        """Update the test configuration and emit the selected material."""
        test_type_uri, _ = self.test_type_selector.currentData()
        test_type_uri = URIRef(test_type_uri) if isinstance(test_type_uri, str) else test_type_uri
        if isinstance(test_type_uri, URIRef) and test_type_uri == self.experiment.DYNAMAT.SpecimenTest:
            material_uri, material_abbreviation = self.material_selector.currentData()
            if material_abbreviation:
                self.test_config.specimen_material = material_uri  # Update global state  
                self.current_specimen_material.emit(material_abbreviation)
        else: return           
      

    #################################################
    ## USER SELECTION FIELD
    ################################################# 
    
    def update_user(self):
        """Update the test configuration and emit the selected user."""
        user_uri, user_abbreviation = self.user_selector.currentData()
        self.test_config.user = user_uri  # Update global state  

    #################################################
    ## TEST TYPE (SPECIMEN/PULSE) SELECTION FIELD
    #################################################
    
    def update_test_type(self):
        """Update the test configuration and emit the selected user."""
        test_type_uri, _ = self.test_type_selector.currentData()
        self.test_config.test_type = test_type_uri  # Update global state
        test_type_uri = URIRef(test_type_uri) if isinstance(test_type_uri, str) else test_type_uri 
        self.current_test_type.emit(test_type_uri)
        
        if isinstance(test_type_uri, URIRef) and test_type_uri == self.experiment.DYNAMAT.PulseTest:
            self.material_selector.setEnabled(False)
            self.material_selector.setCurrentIndex(-1)  # Clear material selection
        else:
            #self.material_selector = self.populate_materials()
            self.material_selector.setEnabled(True)
            SetDefaults(self.ontology_path, self.test_config.specimen_material, self.material_selector)
            
        self.update_test_name()  # Ensure the test name reflects the condition    

    #################################################
    ## TEST MODE (LAB/FEA) SELECTION FIELD
    #################################################
    
    def update_test_mode(self):
        """Update the test configuration and emit the selected user."""
        test_mode, abbreviation = self.test_mode_selector.currentData()
        self.test_config.test_mode = test_mode  # Update global state
        self.current_test_mode.emit(test_mode)
        

    #################################################
    ## TEST TEMPERATURE MODE (RT/HT) SELECTION FIELD
    #################################################
    
    def update_temp_mode(self):
        """Update the test configuration and emit the selected user."""
        temp_mode, abbreviation = self.temp_mode_selector.currentData()
        self.test_config.temp_mode = temp_mode  # Update global state

        


