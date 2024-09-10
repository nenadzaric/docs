import os

class Config:
    TRICKEST_BASE_URL = os.getenv('TRICKEST_BASE_URL', 'https://hive-api.trickest.io/v1')
    TRICKEST_TOKEN = os.getenv('TRICKEST_TOKEN')
    EDITOR_URL =  os.getenv('EDITOR_URL', 'https://editor.staging.trickest.io/preview?workflow_url=https://trickest-public-workflow.s3.eu-central-1.amazonaws.com/')