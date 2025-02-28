class BarConfiguration:
    """Centralized configuration class for shared state management."""
    def __init__(self):
        # Defined Default Values for Bar Description Tab

        # Striker Bar
        self.StrikerBar_Material = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SteelC350"
        self.StrikerBar_OriginalLength_value = 12
        self.StrikerBar_OriginalLength_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Inch"
        self.StrikerBar_OriginalDiameter_value = 0.375
        self.StrikerBar_OriginalDiameter_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Inch"
        self.StrikerBar_OriginalCrossSectionalArea_value = 0.11044
        self.StrikerBar_OriginalCrossSectionalArea_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SquareInches"
        self.StrikerBar_Density_value = 8082.500
        self.StrikerBar_Density_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#KilogramPerCubicMeter"
        self.StrikerBar_ElasticModulus_value = 199.99
        self.StrikerBar_ElasticModulus_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Gigapascal"
        self.StrikerBar_PoissonsRatio_value = 0.29
        self.StrikerBar_PoissonsRatio_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"
        self.StrikerBar_WaveSpeed_value = 4953.321
        self.StrikerBar_WaveSpeed_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#MeterPerSecond"

        # Incident Bar
        self.IncidentBar_Material = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SteelC350"
        self.IncidentBar_OriginalLength_value = 8
        self.IncidentBar_OriginalLength_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Foot"
        self.IncidentBar_OriginalDiameter_value = 0.375
        self.IncidentBar_OriginalDiameter_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Inch"
        self.IncidentBar_OriginalCrossSectionalArea_value = 0.11044
        self.IncidentBar_OriginalCrossSectionalArea_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SquareInches"
        self.IncidentBar_Density_value = 8082.500
        self.IncidentBar_Density_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#KilogramPerCubicMeter"
        self.IncidentBar_ElasticModulus_value = 199.99
        self.IncidentBar_ElasticModulus_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Gigapascal"
        self.IncidentBar_PoissonsRatio_value = 0.29
        self.IncidentBar_PoissonsRatio_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"
        self.IncidentBar_WaveSpeed_value = 4953.321
        self.IncidentBar_WaveSpeed_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#MeterPerSecond"

        # Transmitted Bar 
        self.TransmittedBar_Material = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SteelC350"
        self.TransmittedBar_OriginalLength_value = 6
        self.TransmittedBar_OriginalLength_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Foot"
        self.TransmittedBar_OriginalDiameter_value = 0.375
        self.TransmittedBar_OriginalDiameter_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Inch"
        self.TransmittedBar_OriginalCrossSectionalArea_value = 0.11044
        self.TransmittedBar_OriginalCrossSectionalArea_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SquareInches"
        self.TransmittedBar_Density_value = 8082.500
        self.TransmittedBar_Density_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#KilogramPerCubicMeter"
        self.TransmittedBar_ElasticModulus_value = 199.99
        self.TransmittedBar_ElasticModulus_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Gigapascal"
        self.TransmittedBar_PoissonsRatio_value = 0.29
        self.TransmittedBar_PoissonsRatio_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"
        self.TransmittedBar_WaveSpeed_value = 4953.321
        self.TransmittedBar_WaveSpeed_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#MeterPerSecond"        

    def __getitem__(self, key):
        return getattr(self, key, None)  # Fallback to getattr


