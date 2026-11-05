import os
import sys
import uvicorn

# Ensure both root and api directories are available
root_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.join(root_dir, "api")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

from api.index import app

if __name__ == "__main__":
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)
