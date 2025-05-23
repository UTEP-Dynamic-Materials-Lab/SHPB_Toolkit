class SGConfiguration:
    """Centralized configuration class for shared state management."""
    def __init__(self):

        # Defined Default Values for Strain Gauges Properties

        # SG Calibration Resistance
        self.CalibrationResistance_value = 59.95e3
        self.CalibrationResistance_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Ohms"

        # SG Calibration Voltage
        self.CalibrationVoltage_value = 2
        self.CalibrationVoltage_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Volts"

        # SG Factor
        self.GaugeFactor_value = 2.06
        self.GaugeFactor_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Unitless"

        # SG Resistance
        self.Resistance_value = 120
        self.Resistance_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Ohms"

        # SG Data Acquisition Rate
        self.DataAcquisitionRate_value = 10
        self.DataAcquisitionRate_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#MegaHertz"

        # Default Number of SG: 
        self.Incident_Bar_Gauges = 1
        self.Transmitted_Bar_Gauges = 1

        # Incident Bar Strain Gauge 0 Defaults
        self.IncidentStrainGauge_0_Distance_value = 4.0
        self.IncidentStrainGauge_0_Distance_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Foot"

        # Transmitted Bar Strain Gauge 0 Defaults
        self.TransmittedStrainGauge_0_Distance_value = 4.0
        self.TransmittedStrainGauge_0_Distance_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Foot"
        
    def __getitem__(self, key):
        return getattr(self, key, None)  # Fallback to getattr




