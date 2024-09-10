# main.py
import logging
from config import Config
from api_client import TrickestClient
from services import TrickestService
from file_generators import FileGenerator
import os
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrickestApp:
    def __init__(self):
        self.client = TrickestClient(Config.TRICKEST_BASE_URL, Config.TRICKEST_TOKEN)
        self.service = TrickestService(self.client)
        self.file_generator = FileGenerator()

    def copy_and_delete_library(self):
        source_dir = os.path.join(os.getcwd(), 'library')  # Current directory's "Library" folder
        destination_dir = os.path.abspath(os.path.join(os.getcwd(), '../library'))  # Parent directory

        if not os.path.exists(source_dir):
            logger.error(f"Source directory '{source_dir}' does not exist.")
            return

        try:
            # Copy all directories from Library to parent directory
            for item in os.listdir(source_dir):
                source_item_path = os.path.join(source_dir, item)
                destination_item_path = os.path.join(destination_dir, item)

                # Only copy directories, not individual files
                if os.path.isdir(source_item_path):
                    shutil.copytree(source_item_path, destination_item_path, dirs_exist_ok=True)
                    logger.info(f"Copied directory '{source_item_path}' to '{destination_item_path}'")
                else:
                    logger.info(f"Skipped non-directory item '{source_item_path}'")

            # Delete the Library folder after copying
            shutil.rmtree(source_dir)
            logger.info(f"Deleted the source directory '{source_dir}' after copying.")

            logger.info("All directories from Library successfully copied to parent directory and Library folder deleted.")
        except Exception as e:
            logger.error(f"An error occurred while copying or deleting directories: {e}")
            raise

    # Call this function within your TrickestApp class's run method.


    def run(self):
        try:
            logger.info("Starting Trickest content generation...")

            logger.info("Getting categories...")
            categories = self.service.get_library_categories()
            logger.info(f"Found {len(categories)} categories.")

            logger.info("Getting workflows...")
            workflows = self.service.get_library_workflows()
            logger.info(f"Found {len(workflows)} workflows.")

            logger.info("Getting tools...")
            tools = self.service.get_library_tools()
            logger.info(f"Found {len(tools)} tools.")

            logger.info("Getting modules...")
            modules = self.service.get_library_modules()
            logger.info(f"Found {len(modules)} modules.")

            logger.info("Creating folder structures...")
            self.file_generator.create_folder_structures(categories)

            logger.info("Generating workflow files...")
            self.file_generator.create_mdx_files_workflows(categories, workflows)
            self.file_generator.create_workflow_version_files(self.service, workflows)
            self.file_generator.create_individual_workflow_files(workflows)

            logger.info("Generating tool files...")
            self.file_generator.create_and_save_tool_workflows(tools)
            self.file_generator.create_individual_tool_files(tools)
            self.file_generator.create_mdx_files_tools(categories, tools)

            logger.info("Generating module files...")
            self.file_generator.create_and_save_module_workflows(modules)
            self.file_generator.create_mdx_files_category_modules(categories, modules)
            self.file_generator.create_mdx_files_for_modules(modules)


            self.copy_and_delete_library()
            logger.info("Updating mint.json...")
            self.file_generator.update_mint_json_with_categories(categories)

            logger.info("All operations completed successfully.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

if __name__ == '__main__':
    app = TrickestApp()
    app.run()