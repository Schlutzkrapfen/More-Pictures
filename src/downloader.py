
# Define the URL where Label Studio is accessible
LABEL_STUDIO_URL = 'YOUR_BASE_URL'

# API key can be either your PAT or legacy access token
LABEL_STUDIO_API_KEY = 'YOUR_API_KEY'

# Import the SDK and the client module
from label_studio_sdk import LabelStudio
client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)