# models.py
import re
from datetime import datetime
from typing import Dict, Any

class Workflow:
    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']
        self.name = data['name']
        self.category = data['workflow_category']
        self.description = re.sub(r'[^\x20-\x7E"]|"', '', data['description'])
        self.complexity = data.get('complexity', 1)
        self.publisher = data.get('author', 'Unknown')
        self.created_on = self._format_date(data.get('created_date', ''))

    @staticmethod
    def _format_date(date_str: str) -> str:
        if date_str:
            return datetime.fromisoformat(date_str[:-1]).strftime('%d %B, %Y')
        return 'Unknown'

class Tool:
    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.category = data['tool_category_name']
        self.container = data['container']
        self.inputs = data['inputs']
        self.outputs = data['outputs']
        self.created_date = data['created_date']
        self.author = data.get('author', 'Unknown')
        self.source_url = data.get('source_url', '')
        self.license = data.get('license', 'Unknown')
        self.output_command = data.get('output_command', '')
        self.output_type = data.get('output_type', '')

class Module:
    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.category = data['workflow_category']['name']
        self.inputs = data['inputs']
        self.outputs = data['outputs']
        self.created_date = data['created_date']
        self.author = data['author']
        self.long_description = data['long_description']
        self.workflow = data.get('workflow')