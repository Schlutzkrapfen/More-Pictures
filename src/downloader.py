
import yaml
from label_studio_sdk import LabelStudio

# 1. Load the configuration from your YAML file
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

# 2. Extract values from the 'label_studio' section
LS_URL = config['label_studio']['url']
LS_API_KEY = config['label_studio']['api_key']
PROJECT_ID = config['label_studio']['project_id']

# 3. Extract values from the 'download' section
OUTPUT_DIR = config['download']['output_dir']
ONLY_COMPLETED = config['download']['only_completed']

# 4. Initialize the Client
client = LabelStudio(
    base_url=LS_URL, 
    api_key=LS_API_KEY
)

print(f"Successfully connected to {LS_URL}")
print(f"Ready to work with Project ID: {PROJECT_ID}")