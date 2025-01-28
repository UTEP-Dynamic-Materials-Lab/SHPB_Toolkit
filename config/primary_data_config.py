class PrimaryDataConfiguration:
    """Centralized configuration class for shared state management."""
    def __init__(self):
        # Defined Default Values for Primary Data Tab

        self.IncidentSensorSignal_0_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Volts"
        self.TransmittedSensorSignal_0_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Volts"
        self.TimeSensorSignal_0_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Millisecond"

    def __getitem__(self, key):
        return getattr(self, key, None)  # Fallback to getattr