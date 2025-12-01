import sys
import logging
from fhirpy import SyncFHIRClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FHIR_URL = "http://fhir-server:8080/fhir"

def verify_fhir_connection():
    try:
        logger.info(f"Attempting to connect to FHIR server at {FHIR_URL}...")
        client = SyncFHIRClient(url=FHIR_URL, authorization=None)
        
        # Try to fetch metadata (CapabilityStatement)
        # Note: fhirpy doesn't have a direct metadata method, but we can try to search for a resource
        # or just check if we can create a client without error.
        # A search for patients with a limit of 1 is a good smoke test.
        logger.info("Searching for Patient resources...")
        patients = client.resources('Patient').limit(1).fetch_all()
        
        logger.info("Successfully connected to FHIR server!")
        logger.info(f"Found {len(patients)} patients (limit 1).")
        return True
        
    except Exception as e:
        logger.error(f"Failed to connect to FHIR server: {e}")
        return False

if __name__ == "__main__":
    success = verify_fhir_connection()
    sys.exit(0 if success else 1)
