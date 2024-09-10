# services.py
from typing import List, Dict, Any
from models import Workflow, Tool, Module
from api_client import TrickestClient

class TrickestService:
    def __init__(self, client: TrickestClient):
        self.client = client

    def get_library_workflows(self) -> List[Workflow]:
        response = self.client.get('library/workflow?page_size=500')
        return [Workflow(workflow) for workflow in response['results']]

    def get_library_tools(self) -> List[Tool]:
        response = self.client.get('library/tool?page_size=500')
        tools = []
        for tool_data in response['results']:
            detailed_tool = self.client.get(f'library/tool/{tool_data["id"]}')
            tools.append(Tool(detailed_tool))
        return tools

    def get_library_modules(self) -> List[Module]:
        response = self.client.get('library/module?page_size=500')
        modules = []
        for module_data in response['results']:
            detailed_module = self.client.get(f'library/module/{module_data["id"]}')
            modules.append(Module(detailed_module))
        return modules

    def get_library_categories(self) -> List[Dict[str, Any]]:
        response = self.client.get('library/categories/?page_size=100')
        return response['results']

    def get_library_workflow_version(self, workflow_id: str) -> Dict[str, Any]:
        return self.client.get(f'library/workflow-version/latest/?workflow={workflow_id}')