import uvicorn

from app.runner.asgi import fastapi_app

# couldn't run app from this file, so I extracted main in outer folder

uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, debug=True)
