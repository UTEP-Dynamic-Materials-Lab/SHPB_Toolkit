class TestConfiguration:
    """Centralized configuration class for shared state management."""
    def __init__(self):
        self.is_fea = False  # Tracks whether the test type is FEA
        self.test_condition = "Specimen"  # "Specimen" or "Pulse"
        self.environment = "RT"  # "RT" or "HT"
        self.specimen_material = None  # Selected material abbreviation or None
