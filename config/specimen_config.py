class SpecimenConfiguration:
    """Centralized configuration class for shared state management."""
    def __init__(self):

        # Defined Default Values for Specimen Configuration

        # SHPB Specimen
        self.SHPBSpecimen_MaterialProcessing = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#StockMaterial"
        self.SHPBSpecimen_Shape = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Cylindrical"
        self.SHPBSpecimen_Structure = "https://github.com/UTEP-Dynamic-Materials-Lab/SHPB_Toolkit/tree/main/ontology#Monolithic"

   
    def __getitem__(self, key):
        return getattr(self, key, None)  # Fallback to getattr




