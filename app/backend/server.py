from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.solver_routes import router as solver_router
from routers.solver_routes import ws_router

app = FastAPI(title="Rubik's Cube Solver API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(solver_router)
app.include_router(ws_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
