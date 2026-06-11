from pathlib import Path

import yaml

DEFAULT_CONFIG = {
    "local": {
        # If True, use local files instead of the Label Studio API
        "local": False,
        # Folder containing local images (used when local=True)
        "picture_path": "",
        # Exact path to the local JSON annotation file (used when local=True)
        "json_path": "",
    },
    "label_studio": {
        # The base URL where your Label Studio instance is running
        "url": "",
        # Your API key — Personal Access Token (PAT) or legacy access token
        # Find it under: Account & Settings → Access Token
        "api_key": "",
        # Numeric ID of the project to download images from
        # Found in the URL: /projects/<project_id>/
        "project_id": 2,
    },
    "download": {
        # Folder where downloaded images will be saved
        "output_dir": "output/",
        # True  → only download fully annotated/completed tasks
        # False → download all tasks regardless of annotation status
        "only_completed": True,
    },
    "output": {
        # Save path for the output JSON file.
        # If empty, the path from the source picture will be reused.
        # WARNING: Uploaded pictures will NOT be shown in Label Studio if left empty!
        "json_output_path": "",
        # Folder where augmented pictures should be stored
        "output_label_studio": "",
    },
    "brightness": {
        # List of brightness factors to apply, e.g. [0.5, 1.5]
        "brigtness_list": [],
        # If True, brightness can be combined with other augmentations. (See ImageStatEnum how the )
        "brightness_combination": [False, False, False],
    },
    "gauss": {
        # List of Gaussian blur kernel sizes to apply, e.g. [3, 5]
        "gauss_list": [],
        # If True, Gaussian blur can be combined with other augmentations
        "gauss_combination": [False, False, False],
    },
    "mirrored": {
        # If True, mirrored versions of images will be generated
        "mirrored": True,
        # If True, mirroring can be combined with other augmentations
        "mirrored_combination": [False, False, False],
    },
}


def generate_default_config(output_path: str = "config.yml"):
    try:
        Path(output_path).write_text(
            yaml.dump(DEFAULT_CONFIG, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        print("made a new default yml")
        return output_path
    except Exception as e:
        print(f"Something went wrong with creating a new deafult yml. Error {e}")
        return None
