import logging
import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "cp1252",
    "latin-1",
    "ISO-8859-1"
]

def read_csv_with_encodings(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Attempts to read a CSV file using multiple encodings in order:
    utf-8, utf-8-sig, cp1252, latin-1, ISO-8859-1.
    Logs the successful encoding.
    If all encodings fail, raises a ValueError with a clean, user-friendly message.
    """
    # Check for binary file by looking for null bytes in the first 8KB
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(8192)
            if b"\x00" in chunk:
                raise ValueError("The file appears to be a binary file, not a valid text CSV.")
    except ValueError:
        raise
    except Exception as e:
        logger.debug(f"Failed to check for binary signature in '{file_path}': {str(e)}")

    errors = []
    for encoding in SUPPORTED_ENCODINGS:
        try:
            # Attempt to read the CSV with the current encoding
            df = pd.read_csv(file_path, encoding=encoding, **kwargs)
            logger.info(f"Successfully loaded dataset '{file_path}' using encoding: {encoding}")
            return df
        except Exception as e:
            # Record the error and proceed to the next encoding
            errors.append(f"{encoding}: {str(e)}")
            logger.debug(f"Failed to read '{file_path}' with encoding '{encoding}': {str(e)}")

    # If we reached here, all encodings failed
    error_details = "; ".join(errors)
    logger.error(f"All attempted encodings failed for file '{file_path}'. Errors: {error_details}")
    raise ValueError(
        "Could not decode the CSV file. The file may be corrupted or in an unsupported format. "
        "Supported encodings are: utf-8, utf-8-sig, cp1252, latin-1, ISO-8859-1."
    )
