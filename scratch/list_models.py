import urllib.request
import json
import sys

try:
    req = urllib.request.Request("http://localhost:11434/api/tags")
    with urllib.request.urlopen(req, timeout=3) as res:
        data = json.loads(res.read().decode())
        print("Model data from /api/tags:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error querying local Ollama tags: {e}")
    sys.exit(1)
