import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Union
from datetime import datetime

def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load JSON data from file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """Save data to JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_csv(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load CSV data from file."""
    data = []
    with open(file_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(dict(row))
    return data

def save_csv(data: List[Dict[str, Any]], file_path: Union[str, Path]) -> None:
    """Save data to CSV file."""
    if not data:
        return
    
    fieldnames = data[0].keys()
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def format_timestamp(dt: datetime = None) -> str:
    """Format datetime as string."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None