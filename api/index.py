import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from main import app
except Exception as e:
    import traceback
    from fastapi import FastAPI
    app = FastAPI()
    err_msg = f"{type(e).__name__}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
    
    @app.get("/{full_path:path}")
    def catch_all(full_path: str):
        return {"error": "Import error during initialization", "details": err_msg}
