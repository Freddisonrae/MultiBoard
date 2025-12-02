from fastapi import FastAPI
def create_app() -> FastAPI:
    app = FastAPI(title="MultiBoard Server")
    # app.include_router(api_router)


