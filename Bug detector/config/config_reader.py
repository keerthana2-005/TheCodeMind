import json
import os

CONFIG_PATH = "config/config.json"  # Ensure the file exists

def read_config():
    """Reads the API key from a JSON config file."""
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Config file not found. Please create config/config.json"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in config file. Check formatting."}
