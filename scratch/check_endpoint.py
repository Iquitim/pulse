import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app.routes.ollama import normalize_host
from ollama import Client

try:
    normalized_host = normalize_host("http://localhost:11434")
    client = Client(host=normalized_host)
    models_data = client.list()
    
    print("Testing response.models:")
    models = getattr(models_data, 'models', [])
    print(f"Models list: {models}")
    
    names = []
    for m in models:
        # Try m.model or m.name or dictionary access
        model_name = getattr(m, 'model', None) or getattr(m, 'name', None)
        if model_name:
            names.append(model_name)
            
    print(f"Resolved names: {names}")
except Exception as e:
    print(f"Error: {e}")
