import os
from rdflib import Graph, Namespace, URIRef
from scripts.rdf_wrapper import RDFWrapper
from scripts.SHPB_SignalExtract import SignalExtractor
from scripts.SHPB_SeriesData import SeriesData
from scripts.validator import ValidateData

DATABASE_FOLDER = "data"
ONTOLOGY_PATH = "ontology/DynaMat_SHPB.ttl"

def clear_secondary_data(experiment):
    """
    Removes all triples related to secondary data from the RDF file.
    """
    secondary_instance = experiment.get_instances_of_class(f"dynamat:SecondaryData")[0]
    experiment.remove((URIRef(secondary_instance), URIRef(experiment.DYNAMAT.hasExtractedSignal), None))
    experiment.remove((URIRef(secondary_instance), URIRef(experiment.DYNAMAT.hasPulseProperty), None))
    experiment.remove((URIRef(secondary_instance), URIRef(experiment.DYNAMAT.hasSeriesData), None))

def process_file(file_path):
    """
    Processes a single RDF file:
    - Clears existing secondary data.
    - Performs unit conversion.
    - Validates metadata, test type, mode, and temperature.
    - Extracts signals and determines series data.
    - Saves the updated file back to the database.
    """
    # Load RDF data
    experiment = RDFWrapper(file_path)   

    # Clear secondary data before reanalysis
    clear_secondary_data(experiment)
    with open(file_path, "w") as f:
        f.write(experiment.serialize("turtle"))   
    
    # Extract metadata
    metadata = experiment.get_instances_of_class("dynamat:Metadata")[0]
    test_name = experiment.get_objects(metadata, "dynamat:hasTestName")[0]
    testing_conditions = experiment.get_instances_of_class("dynamat:TestingConditions")[0]
    test_type = experiment.get_objects(testing_conditions, "dynamat:hasTestType")[0]
    test_temperature = experiment.get_objects(testing_conditions, "dynamat:hasTestTemperature")[0]
    
    print(f"\n Starting secondary data analysis for {test_name}...")
    SignalExtractor(ONTOLOGY_PATH, file_path)
    
    if URIRef(test_type) == experiment.DYNAMAT.SpecimenTest:
        print(f"\n Determining series data for specimen test: {test_name}")
        SeriesData(ONTOLOGY_PATH, file_path)

    print(f"Updating {file_path} with new secondary data...")
    print()

def update_all_files():
    """
    Loops through all RDF files in the database folder and updates secondary data.
    """
    print("Starting batch update for all RDF files in the database...")

    for filename in os.listdir(DATABASE_FOLDER)[-5:]:
        if filename.endswith(".ttl"):
            file_path = os.path.join(DATABASE_FOLDER, filename)
            process_file(file_path)

    print("Batch update complete.")

if __name__ == "__main__":
    update_all_files()
