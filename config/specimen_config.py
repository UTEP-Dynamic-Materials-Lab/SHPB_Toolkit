class SpecimenConfiguration:
    """Centralized configuration class for shared state management."""
    def __init__(self):

        # Defined Default Values for Specimen Configuration

        # SHPB Specimen
        self.SHPBSpecimen_SpecimenProcessing = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#MachiningProcess"
        self.SHPBSpecimen_Shape = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Cylindrical"
        self.SHPBSpecimen_Structure = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Monolithic"

        # SHPB Specimen Dimension Units

        self.SHPBSpecimen_DeformedCrossSectionalArea_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SquareMilimeters"
        self.SHPBSpecimen_DeformedLength_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Millimeter"
        self.SHPBSpecimen_DeformedDiameter_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Millimeter"
        self.SHPBSpecimen_OriginalCrossSectionalArea_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#SquareMilimeters"
        self.SHPBSpecimen_OriginalLength_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Millimeter" 
        self.SHPBSpecimen_OriginalDiameter_units = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Millimeter"
  
    def __getitem__(self, key):
        return getattr(self, key, None)  # Fallback to getattr




