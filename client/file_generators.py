import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any
from models import Workflow, Tool, Module
from config import Config
from jinja2 import Environment, FileSystemLoader

class FileGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates'))

    @staticmethod
    def create_folder_structures(categories: List[Dict[str, Any]]):
        for category in categories:
            base_path = f'library/{category["name"].replace(" ", "-").lower()}'
            has_workflows = category.get('workflow_count', 0) > 0
            has_tools = category.get('tool_count', 0) > 0
            has_modules = category.get('module_count', 0) > 0

            if has_workflows or has_tools or has_modules:
                os.makedirs(base_path, exist_ok=True)
                if has_workflows:
                    os.makedirs(f'{base_path}/workflows', exist_ok=True)
                if has_tools:
                    os.makedirs(f'{base_path}/tools', exist_ok=True)

    def create_mdx_files_workflows(self, categories: List[Dict[str, Any]], workflows: List[Workflow]):
        template = self.env.get_template('workflow_list_template.template')
        for category in categories:
            base_path = f'library/{category["name"].replace(" ", "-").lower()}'
            category_workflows = [w for w in workflows if w.category == category["name"]]
            
            if category_workflows:
                workflow_data = []
                for workflow in category_workflows:
                    workflow_data.append({
                        'name': workflow.name,
                        'description': workflow.description,
                        'iframe_url': f"{Config.EDITOR_URL}{workflow.id}.json",
                        'href': f"/library/{workflow.category.replace(' ', '-').lower()}/workflows/{workflow.name.replace(' ', '-').lower()}",
                        'id': workflow.id,
                        'category': workflow.category,
                        'complexity': f"{{{workflow.complexity}}}",  # This will render as {3}, {2}, etc.
                        'publisher': workflow.publisher
                    })

                mdx_content = template.render(
                    category_name=category['name'],
                    workflows=workflow_data
                )
                
                os.makedirs(base_path, exist_ok=True)
                with open(f'{base_path}/workflows.mdx', 'w') as mdx_file:
                    mdx_file.write(mdx_content)
    @staticmethod
    def create_workflow_version_files(service, workflows: List[Workflow]):
        os.makedirs('s3', exist_ok=True)
        for workflow in workflows:
            workflow_version = service.get_library_workflow_version(workflow.id)
            with open(f's3/{workflow.id}.json', 'w') as file:
                json.dump(workflow_version, file, indent=2)

    def create_individual_workflow_files(self, workflows: List[Workflow]):
        template = self.env.get_template('individual_workflow_template.template')
        for workflow in workflows:
            category_name = workflow.category.replace(" ", "-").lower()
            workflow_name = workflow.name.replace(" ", "-").lower()
            workflow_path = f'library/{category_name}/workflows/{workflow_name}.mdx'
            
            mdx_content = template.render(
                name=workflow.name,
                description=workflow.description,
                category=workflow.category,
                created_on=workflow.created_on,
                publisher=workflow.publisher,
                workflow_url=f"{Config.EDITOR_URL}{workflow.id}.json",
                id=workflow.id
            )

            os.makedirs(f'library/{category_name}/workflows', exist_ok=True)
            with open(workflow_path, 'w') as mdx_file:
                mdx_file.write(mdx_content)

    @staticmethod
    def create_and_save_tool_workflows(tools: List[Tool]):
        output_folder = 's3'
        os.makedirs(output_folder, exist_ok=True)

        for tool in tools:
            workflow = {
                "id": str(uuid.uuid4()),
                "name": None,
                "description": None,
                "workflow_info": str(uuid.uuid4()),
                "created_date": datetime.utcnow().isoformat() + "Z",
                "run_count": 0,
                "data": {
                    "nodes": {
                        f"{tool.name}-1": {
                            "id": tool.id,
                            "meta": {
                                "label": tool.name,
                                "coordinates": {"x": 6136, "y": 2696}
                            },
                            "name": f"{tool.name}-1",
                            "type": "TOOL",
                            "inputs": tool.inputs,
                            "outputs": tool.outputs,
                            "bee_type": "small",
                            "container": tool.container,
                            "created_date": tool.created_date,
                            "output_command": tool.output_command,
                            "tool_category_name": tool.category
                        }
                    },
                    "annotations": {},
                    "connections": [],
                    "outputNodes": {},
                    "primitiveNodes": {}
                },
                "snapshot": False
            }

            with open(f'{output_folder}/{tool.id}.json', 'w') as file:
                json.dump(workflow, file, indent=2)

    def _escape_description(self, description: str) -> str:
        return description.replace('"', '').replace('\n', '').replace('\r', '')

    def create_mdx_files_tools(self, categories: List[Dict[str, Any]], tools: List[Tool]):
        template = self.env.get_template('tool_list_template.template')
        for category in categories:
            base_path = f'library/{category["name"].replace(" ", "-").lower()}'
            category_tools = [tool for tool in tools if tool.category == category["name"]]
            
            if category_tools:
                tool_data = []
                for tool in category_tools:
                    tool_data.append({
                        'name': tool.name,
                        'description': self._escape_description(tool.description),
                        'iframe_url': f"{Config.EDITOR_URL}{tool.id}.json",
                        'href': f"/library/{tool.category.replace(' ', '-').lower()}/tools/{tool.name.replace(' ', '-').lower()}",
                        'category': tool.category
                    })

                mdx_content = template.render(
                    category_name=category['name'],
                    tools=tool_data
                )
                
                with open(f'{base_path}/tools.mdx', 'w') as mdx_file:
                    mdx_file.write(mdx_content)

    def create_individual_tool_files(self, tools: List[Tool]):
        template = self.env.get_template('individual_tool_template.template')
        for tool in tools:
            category_name = tool.category.replace(" ", "-").lower()
            tool_name = tool.name.replace(" ", "-").lower()
            tool_path = f'library/{category_name}/tools/{tool_name}.mdx'

            # Format inputs
            inputs_formatted = "{ {\n"
            for input_name, input_data in tool.inputs.items():
                inputs_formatted += f'  "{input_name}": {{\n'
                for key, value in input_data.items():
                    if isinstance(value, str):
                        inputs_formatted += f'    "{key}": "{self._escape_description(value)}",\n'
                    elif isinstance(value, bool):
                        inputs_formatted += f'    "{key}": {str(value).lower()},\n'
                    else:
                        inputs_formatted += f'    "{key}": {json.dumps(value)},\n'
                inputs_formatted += "  },\n"
            inputs_formatted += "}}"

            mdx_content = template.render(
                id=tool.id,
                name=tool.name,
                description=self._escape_description(tool.description),
                category=tool.category,
                author=tool.author,
                created_date=tool.created_date[:10],
                container=tool.container['image'],
                source_url=tool.source_url,
                license=tool.license,
                output_command=self._escape_description(tool.output_command),
                output_type=tool.output_type,
                iframe_url=f"{Config.EDITOR_URL}{tool.id}.json",
                inputs=inputs_formatted
            )

            os.makedirs(f'library/{category_name}/tools', exist_ok=True)
            with open(tool_path, 'w') as mdx_file:
                mdx_file.write(mdx_content)

    @staticmethod
    def create_and_save_module_workflows(modules: List[Module]):
        output_folder = 's3'
        os.makedirs(output_folder, exist_ok=True)

        for module in modules:
            workflow = {
                "id": str(uuid.uuid4()),
                "name": None,
                "description": None,
                "workflow_info": module.workflow or str(uuid.uuid4()),
                "created_date": datetime.utcnow().isoformat() + "Z",
                "run_count": 0,
                "data": {
                    "nodes": {
                        f"{module.name.replace(' ', '-').lower()}-1": {
                            "id": module.id,
                            "meta": {
                                "label": module.name,
                                "coordinates": {"x": 6192, "y": 3096.000244140625}
                            },
                            "name": f"{module.name.replace(' ', '-').lower()}-1",
                            "type": "WORKFLOW",
                            "inputs": {k: {
                                "type": v["type"],
                                "multi": True,
                                "order": 0,
                                "visible": v["visible"],
                                "description": v["description"]
                            } for k, v in module.inputs.items()},
                            "outputs": {v["parameter_name"]: {
                                "type": v["type"],
                                "order": 0,
                                "visible": v.get("visible", False),
                                "parameter_name": v["parameter_name"]
                            } for v in module.outputs.values()},
                            "bee_type": "small",
                            "workflow": module.workflow,
                            "created_date": module.created_date,
                            "workflow_category": {
                                "id": module.category,
                                "name": module.category,
                                "description": ""
                            }
                        }
                    },
                    "annotations": {},
                    "connections": [],
                    "outputNodes": {},
                    "primitiveNodes": {}
                },
                "snapshot": False
            }

            with open(f'{output_folder}/{module.id}.json', 'w') as file:
                json.dump(workflow, file, indent=2)

    def create_mdx_files_category_modules(self, categories: List[Dict[str, Any]], modules: List[Module]):
        template = self.env.get_template('module_list_template.template')
        base_path = 'library/modules'
        os.makedirs(base_path, exist_ok=True)

        for category in categories:
            category_modules = [module for module in modules if module.category == category["name"]]
            
            if category_modules:
                category_file_path = f'{base_path}/{category["name"].replace(" ", "-").lower()}.mdx'
                
                module_data = []
                for module in category_modules:
                    module_data.append({
                        'name': module.name,
                        'category': module.category,
                        'inputs': f"{{{json.dumps(list(module.inputs.keys()))}}}",
                        'outputs': f"{{{json.dumps([output['parameter_name'] for output in module.outputs.values()])}}}",
                        'description': self._escape_description(module.description),
                        'author': module.author,
                        'created_date': module.created_date[:10],
                        'iframe_url': f"{Config.EDITOR_URL}{module.id}.json"
                    })

                mdx_content = template.render(
                    category_name=category['name'],
                    modules=module_data
                )
                
                with open(category_file_path, 'w') as mdx_file:
                    mdx_file.write(mdx_content)

    def create_mdx_files_for_modules(self, modules: List[Module]):
        template = self.env.get_template('individual_module_template.template')
        base_dir = 'library/modules/'
        os.makedirs(base_dir, exist_ok=True)

        for module in modules:
            category_dir = os.path.join(base_dir, module.category.replace(' ', '-').lower())
            os.makedirs(category_dir, exist_ok=True)

            mdx_file_path = os.path.join(category_dir, f"{module.name.replace(' ', '-').lower()}.mdx")

            # Format inputs
            inputs_formatted = "{ {\n"
            for input_name, input_data in module.inputs.items():
                inputs_formatted += f'  "{input_name}": {{\n'
                for key, value in input_data.items():
                    if key == "description" and isinstance(value, str):
                        # Use _escape_description for descriptions
                        value = self._escape_description(value)
                        inputs_formatted += f'    "{key}": "{value}",\n'
                    elif isinstance(value, str):
                        inputs_formatted += f'    "{key}": "{value}",\n'
                    elif isinstance(value, bool):
                        inputs_formatted += f'    "{key}": {str(value).lower()},\n'
                    else:
                        inputs_formatted += f'    "{key}": {json.dumps(value)},\n'
                inputs_formatted += "  },\n"
            inputs_formatted += "}}"

            # Format outputs
            outputs_formatted = "{[ \n"
            outputs_formatted += ",\n".join(f'    "{output["parameter_name"]}"' for output in module.outputs.values())
            outputs_formatted += "\n  ]}"

            mdx_content = template.render(
                name=module.name,
                description=module.description,
                category=module.category,
                inputs=inputs_formatted,
                outputs=outputs_formatted,
                author=module.author,
                created_date=module.created_date[:10],
                iframe_url=f"{Config.EDITOR_URL}{module.id}.json",
                long_description=module.long_description
            )

            with open(mdx_file_path, 'w') as mdx_file:
                mdx_file.write(mdx_content)

    @staticmethod
    def update_mint_json_with_categories(categories: List[Dict[str, Any]]):
        mint_json_path = '../mint.json'

        with open(mint_json_path, 'r') as file:
            mint_data = json.load(file)

        navigation = mint_data.get("navigation", [])
        library_group = next((group for group in navigation if isinstance(group, dict) and group.get("group") == "Library"), None)

        if not library_group:
            library_group = {"group": "Library", "pages": []}
            navigation.append(library_group)

        library_pages = library_group["pages"]

        for category in categories:
            category_name = category['name']
            workflow_count = category.get('workflow_count', 0)
            tool_count = category.get('tool_count', 0)
            module_count = category.get('module_count', 0)

            category_base_path = f"library/{category_name.replace(' ', '-').lower()}"
            workflow_introduction_path = f"{category_base_path}/workflows"
            tools_introduction_path = f"{category_base_path}/tools"

            existing_category_group = next((item for item in library_pages if isinstance(item, dict) and item.get("group") == category_name), None)

            if not existing_category_group:
                category_group = {"group": category_name, "pages": []}
                library_pages.append(category_group)
            else:
                category_group = existing_category_group

            if workflow_count > 0 and workflow_introduction_path not in category_group["pages"]:
                category_group["pages"].append(workflow_introduction_path)

            if tool_count > 0 and tools_introduction_path not in category_group["pages"]:
                category_group["pages"].append(tools_introduction_path)

        modules_group = next((group for group in library_pages if isinstance(group, dict) and group.get("group") == "Modules"), None)

        if not modules_group:
            modules_group = {"group": "Modules", "pages": []}
            library_pages.insert(0, modules_group)

        for category in categories:
            category_name = category['name']
            module_count = category.get('module_count', 0)
            module_path = f"library/modules/{category_name.replace(' ', '-').lower()}"

            if module_count > 0 and module_path not in modules_group["pages"]:
                modules_group["pages"].append(module_path)

        mint_data["navigation"] = navigation

        with open(mint_json_path, 'w') as file:
            json.dump(mint_data, file, indent=2)