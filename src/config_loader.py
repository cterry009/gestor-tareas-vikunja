# src/config_loader.py
import yaml
import os

DEFAULT_CONFIG_PATH = "config/config.yaml"

def load_config(path=DEFAULT_CONFIG_PATH):
    """
    Carga la configuración desde un archivo YAML y retorna un diccionario.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")

    with open(path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)  # parsea YAML y retorna dict
    
    return config_data
