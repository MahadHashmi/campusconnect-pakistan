import os
import sys

# Ensure root directory is first in sys.path for serverless execution
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from main import app
except Exception as e:
    import traceback
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()
    err_trace = traceback.format_exc()

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    def catch_all(full_path: str = ""):
        return JSONResponse(
            status_code=500,
            content={"error": "FastAPI initialization failed", "detail": str(e), "traceback": err_trace}
        )

    @app.api_route("/", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    def catch_root():
        return JSONResponse(
            status_code=500,
            content={"error": "FastAPI initialization failed", "detail": str(e), "traceback": err_trace}
        )
