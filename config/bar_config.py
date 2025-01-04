# bar_config.py
DEFAULT_BAR_CONFIG = {
    "IncidentBar": {
        "dimensions": {
            "Length": {"value": 1.2, "unit": "m"},
            "Cross Sectional Area": {"value": 0.003, "unit": "m^2"},
            "Strain Gauge Distance": {"value": 0.5, "unit": "m"},
        },
        "mechanical_properties": {
            "Elastic Modulus": {"value": 200e9, "unit": "Pa"},
            "Poisson's Ratio": {"value": 0.3, "unit": None},
            "Density": {"value": 7850, "unit": "kg/m^3"},
            "Wave Speed": {"value": 5100, "unit": "m/s"},
        },
    },
    "TransmittedBar": {
        "dimensions": {
            "Length": {"value": 1.5, "unit": "m"},
            "Cross Sectional Area": {"value": 0.004, "unit": "m^2"},
            "Strain Gauge Distance": {"value": 0.7, "unit": "m"},
        },
        "mechanical_properties": {
            "Elastic Modulus": {"value": 190e9, "unit": "Pa"},
            "Poisson's Ratio": {"value": 0.29, "unit": None},
            "Density": {"value": 7800, "unit": "kg/m^3"},
            "Wave Speed": {"value": 5200, "unit": "m/s"},
        },
    },
    "StrikerBar": {
        "dimensions": {
            "Length": {"value": 0.8, "unit": "m"},
            "Cross Sectional Area": {"value": 0.002, "unit": "m^2"},
            "Strain Gauge Distance": {"value": 0.3, "unit": "m"},
        },
        "mechanical_properties": {
            "Elastic Modulus": {"value": 210e9, "unit": "Pa"},
            "Poisson's Ratio": {"value": 0.28, "unit": None},
            "Density": {"value": 7900, "unit": "kg/m^3"},
            "Wave Speed": {"value": 5000, "unit": "m/s"},
        },
    },
}
