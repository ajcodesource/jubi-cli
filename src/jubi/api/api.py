from fastapi import FastAPI, status
from jubi.api.routes.jobs_route import router as jobs_router
from jubi.api.routes.resume_route import router as resume_router


app = FastAPI()
app.include_router(jobs_router)
app.include_router(resume_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Jubi"}


@app.get("/health")
async def health(status_code=status.HTTP_200_OK):
    return {"status": "ok", "status_code": status_code}
