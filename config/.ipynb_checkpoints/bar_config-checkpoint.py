class BarConfiguration:
    """Centralized configuration class for shared state management."""
    def __init__(self):
        # Defined Default Values for Bar Description Tab

        # Striker Bar
        self.StrikerBar_Material = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SteelC350"
        self.StrikerBar_Length_value = 12
        self.StrikerBar_Length_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Inch"
        self.StrikerBar_CrossSectionalArea_value = 0.11044
        self.StrikerBar_CrossSectionalArea_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SquareInches"
        self.StrikerBar_Density_value = 8082.500
        self.StrikerBar_Density_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#KilogramPerCubicMeter"
        self.StrikerBar_ElasticModulus_value = 199.99
        self.StrikerBar_ElasticModulus_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Gigapascal"
        self.StrikerBar_PoissonsRatio_value = 0.29
        self.StrikerBar_PoissonsRatio_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"
        self.StrikerBar_WaveSpeed_value = 4973.770
        self.StrikerBar_WaveSpeed_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#MeterPerSecond"

        # Incident Bar
        self.IncidentBar_Material = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SteelC350"
        self.IncidentBar_Length_value = 8
        self.IncidentBar_Length_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Foot"
        self.IncidentBar_CrossSectionalArea_value = 0.11044
        self.IncidentBar_CrossSectionalArea_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SquareInches"
        self.IncidentBar_StrainGaugeDistance_value = 4
        self.IncidentBar_StrainGaugeDistance_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Foot"
        self.IncidentBar_Density_value = 8082.500
        self.IncidentBar_Density_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#KilogramPerCubicMeter"
        self.IncidentBar_ElasticModulus_value = 199.99
        self.IncidentBar_ElasticModulus_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Gigapascal"
        self.IncidentBar_PoissonsRatio_value = 0.29
        self.IncidentBar_PoissonsRatio_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"
        self.IncidentBar_WaveSpeed_value = 4973.770
        self.IncidentBar_WaveSpeed_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#MeterPerSecond"

        # Transmitted Bar 
        self.TransmittedBar_Material = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SteelC350"
        self.TransmittedBar_Length_value = 6
        self.TransmittedBar_Length_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Foot"
        self.TransmittedBar_CrossSectionalArea_value = 0.11044
        self.TransmittedBar_CrossSectionalArea_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SquareInches"
        self.TransmittedBar_StrainGaugeDistance_value = 4
        self.TransmittedBar_StrainGaugeDistance_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Foot"
        self.TransmittedBar_Density_value = 8082.500
        self.TransmittedBar_Density_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#KilogramPerCubicMeter"
        self.TransmittedBar_ElasticModulus_value = 199.99
        self.TransmittedBar_ElasticModulus_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Gigapascal"
        self.TransmittedBar_PoissonsRatio_value = 0.29
        self.TransmittedBar_PoissonsRatio_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"
        self.TransmittedBar_WaveSpeed_value = 4973.770
        self.TransmittedBar_WaveSpeed_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#MeterPerSecond"        

    def __getitem__(self, key):
        return getattr(self, key, None)  # Fallback to getattr


