import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.create_tables import create_tables
from app.api.mission_controller import router as mission_router
from app.api.ordre_controller import router as order_router
from app.api.rapport_controller import router as rapport_router
from app.api.financement_controller import router as financement_router
from app.api.justificatif_controller import router as justificatif_router
from app.api.hebergement_controller import router as hebergement_router
from app.api.ligne_budgetaire_controller import router as ligne_budgetaire_router
from app.api.remboursement_controller import router as remboursement_router
from app.api.voyage_controller import router as voyage_router
from app.middleware.jwt_check import VerifyInternalJWTMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8000/']
)
app.add_middleware(VerifyInternalJWTMiddleware)

routers = [mission_router, order_router, rapport_router, financement_router, justificatif_router,
           hebergement_router, ligne_budgetaire_router,remboursement_router,voyage_router]

for router in routers:
    app.include_router(router)


@app.on_event("startup")
async def on_startup():
    await create_tables()

@app.get("/home")
async def root():
    return {"message": "Hello World"}





