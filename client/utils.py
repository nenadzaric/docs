import os
import json
import re
from datetime import datetime
import uuid
import logging
from typing import Any, Dict

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_string(s: str) -> str:
    return re.sub(r'[^\x20-\x7E]|"', '', s)

def ensure_directory(path: str):
    os.makedirs(path, exist_ok=True)

def write_json(data: Dict[str, Any], filepath: str):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def write_mdx(content: str, filepath: str):
    with open(filepath, 'w') as f:
        f.write(content)

def format_date(date_string: str) -> str:
    return datetime.fromisoformat(date_string[:-1]).strftime('%d %B, %Y')

def generate_uuid() -> str:
    return str(uuid.uuid4())