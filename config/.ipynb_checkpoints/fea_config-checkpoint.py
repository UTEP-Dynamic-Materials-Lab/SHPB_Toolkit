class FEAConfiguration:
    """Centralized configuration class for shared state management."""
    def __init__(self):
        # Defined Default Values for FEA Strength Model Tabs

        # Striker Bar FEA Model
        self.StrikerBar_Model = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#ElasticStrengthModel"
        self.StrikerBar_Density_value = 8082.500
        self.StrikerBar_Density_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#KilogramPerCubicMeter"
        self.StrikerBar_ElasticModulus_value = 199.99
        self.StrikerBar_ElasticModulus_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Gigapascal"
        self.StrikerBar_PoissonsRatio_value = 0.29
        self.StrikerBar_PoissonsRatio_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"

        # Incident Bar FEA Model
        self.IncidentBar_Model = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#ElasticStrengthModel"
        self.IncidentBar_Density_value = 8082.500
        self.IncidentBar_Density_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#KilogramPerCubicMeter"
        self.IncidentBar_ElasticModulus_value = 199.99
        self.IncidentBar_ElasticModulus_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Gigapascal"
        self.IncidentBar_PoissonsRatio_value = 0.29
        self.IncidentBar_PoissonsRatio_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"

        # Transmitted Bar FEA Model 
        self.TransmittedBar_Material = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#ElasticStrengthModel"
        self.TransmittedBar_Density_value = 8082.500
        self.TransmittedBar_Density_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#KilogramPerCubicMeter"
        self.TransmittedBar_ElasticModulus_value = 199.99
        self.TransmittedBar_ElasticModulus_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Gigapascal"
        self.TransmittedBar_PoissonsRatio_value = 0.29
        self.TransmittedBar_PoissonsRatio_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"

        # Specimen FEA Model
        self.FEASpecimen_Model = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#JohnsonCookModelSimplified"
        self.FEASpecimen_Density_value = 8082.500
        self.FEASpecimen_Density_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#KilogramPerCubicMeter"
        self.FEASpecimen_ElasticModulus_value = 199.99
        self.FEASpecimen_ElasticModulus_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Gigapascal"
        self.FEASpecimen_PoissonsRatio_value = 0.29
        self.FEASpecimen_PoissonsRatio_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"
        ## Need to add the rest of JC Params here...

    
    def __getitem__(self, key):
        return getattr(self, key, None)  # Fallback to getattr


