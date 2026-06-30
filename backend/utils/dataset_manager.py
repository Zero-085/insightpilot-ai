import os
import uuid
import shutil
import pandas as pd
from typing import Dict, Any, Optional
from backend.utils.csv_reader import read_csv_with_encodings

class DatasetManager:
    """
    Manages uploaded datasets in-memory and saves them to a temp folder.
    Provides safety checks, schema descriptions, and path lookups.
    """

    def __init__(self, upload_dir: str = None) -> None:
        if upload_dir is None:
            # Default to backend/temp_uploads
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.upload_dir = os.path.join(base_dir, "temp_uploads")
        else:
            self.upload_dir = upload_dir

        os.makedirs(self.upload_dir, exist_ok=True)
        # Store dataset metadata: {dataset_id: {id, original_name, raw_path, clean_path, status}}
        self._datasets: Dict[str, Dict[str, Any]] = {}
        # Track the ID of the most recently uploaded dataset
        self._latest_dataset_id: Optional[str] = None

    def save_dataset(self, filename: str, content_bytes: bytes) -> str:
        """
        Saves the uploaded CSV content to the upload directory and returns its unique ID.
        """
        if not filename.lower().endswith('.csv'):
            raise ValueError("Only CSV files are accepted.")

        dataset_id = str(uuid.uuid4())
        raw_filename = f"{dataset_id}_raw_{filename}"
        raw_path = os.path.join(self.upload_dir, raw_filename)

        with open(raw_path, "wb") as f:
            f.write(content_bytes)

        # Validate that it can be parsed by pandas
        try:
            read_csv_with_encodings(raw_path, nrows=5)
        except Exception as e:
            if os.path.exists(raw_path):
                os.remove(raw_path)
            raise ValueError(f"Invalid CSV structure: {str(e)}")

        self._datasets[dataset_id] = {
            "id": dataset_id,
            "original_name": filename,
            "raw_path": raw_path,
            "clean_path": None,
            "status": "raw"
        }
        self._latest_dataset_id = dataset_id
        return dataset_id

    def get_dataset(self, dataset_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves dataset metadata. If no ID is provided, returns the latest uploaded.
        """
        target_id = dataset_id or self._latest_dataset_id
        if not target_id or target_id not in self._datasets:
            return None
        return self._datasets[target_id]

    def set_clean_path(self, dataset_id: str, clean_path: str) -> None:
        """
        Updates the dataset info with the cleaned file path.
        """
        if dataset_id in self._datasets:
            self._datasets[dataset_id]["clean_path"] = clean_path
            self._datasets[dataset_id]["status"] = "cleaned"

    def cleanup(self) -> None:
        """
        Deletes all uploaded files and clears the database cache.
        """
        if os.path.exists(self.upload_dir):
            shutil.rmtree(self.upload_dir)
        os.makedirs(self.upload_dir, exist_ok=True)
        self._datasets.clear()
        self._latest_dataset_id = None

# Global instance of the dataset manager
dataset_manager = DatasetManager()
