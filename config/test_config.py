class TestConfiguration:
    """Centralized configuration class for shared state management."""
    def __init__(self):
        # Defined Default Values for Test Description Tab
        self.test_name = None # Do not change! Generate one using the GUI
        self.specimen_material = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SS316"
        self.test_type = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SpecimenTest"
        self.test_mode = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#LABMode"
        self.temp_mode = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#RoomTemperature"

        # Striker Conditions Defaults
        self.momentum_trap_condition = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#MomentumTrapNotEngaged"
        self.striker_velocity_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#MeterPerSecond"
        self.striker_pressure_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Psi"